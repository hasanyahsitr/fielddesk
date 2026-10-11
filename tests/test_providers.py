"""Provider contracts and privacy checks. Synthetic secrets; no external API calls."""
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import time
import unittest
import urllib.error
from unittest.mock import patch, MagicMock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'app'))
import providers
import server

SECRET = 'synthetic-key-not-a-real-credential'
REPLY = {'choices': [{'message': {'content': 'Synthetic answer'}, 'finish_reason': 'stop'}], 'usage': {'total_tokens': 12}}


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.p = providers.Providers(self.root)
    def tearDown(self):
        self.temp.cleanup()
    def save(self, ident='nvidia', **kwargs):
        return self.p.save(dict(provider=ident, key=SECRET, model='test-model', **kwargs))

    def test_session_keys_never_in_snapshot_or_files_and_no_startup_network(self):
        with patch.object(providers, 'transport') as network:
            self.save()
            self.assertNotIn(SECRET, json.dumps(self.p.snapshot()))
            self.assertFalse(self.p.path.exists())
            self.assertFalse(providers.Providers(self.root).snapshot()['providers'][0]['configured'])
            network.assert_not_called()

    @unittest.skipUnless(os.name == 'nt', 'Windows DPAPI')
    def test_windows_encrypted_roundtrip_forget_and_session_downgrade(self):
        self.save(remember=True)
        self.assertNotIn(SECRET.encode(), self.p.path.read_bytes())
        restored = providers.Providers(self.root)
        self.assertEqual(SECRET, restored.config('nvidia')['key'])
        restored.save({'provider': 'nvidia', 'key': '', 'model': 'test-model', 'remember': False})
        self.assertFalse(restored.path.exists())
        restored.save({'provider': 'nvidia', 'key': '', 'model': 'test-model', 'remember': True})
        restored.forget('nvidia')
        self.assertFalse(restored.path.exists())
        with self.assertRaises(ValueError): restored.config('nvidia')

    def test_unreadable_encrypted_key_requires_reentry(self):
        self.p.path.parent.mkdir(parents=True)
        self.p.path.write_bytes(b'invalid synthetic encrypted data')
        with patch.object(providers, 'protect', side_effect=ValueError('failure')):
            restored = providers.Providers(self.root)
        self.assertTrue(restored.warning)
        self.assertFalse(any(x['configured'] for x in restored.snapshot()['providers']))

    def test_protocols_auth_output_caps_and_no_provider_fallback(self):
        for ident, preset in providers.PRESETS.items():
            with self.subTest(provider=ident):
                self.save(ident, **({'base': 'https://example.com/v1'} if ident == 'custom' else {}))
                reply = {'content': [{'type':'text','text':'Synthetic answer'}], 'stop_reason': 'end_turn'} if ident == 'anthropic' else REPLY
                with patch.object(providers, 'transport', return_value=reply) as network:
                    result = self.p.chat(ident, 'test-model', [], 'Synthetic question')
                url, headers, body = network.call_args.args
                self.assertEqual('Synthetic answer', result['answer'])
                self.assertEqual('test-model', body['model'])
                self.assertFalse(body['stream'])
                if ident == 'anthropic':
                    self.assertTrue(url.endswith('/messages'))
                    self.assertEqual(SECRET, headers['x-api-key'])
                    self.assertEqual('2023-06-01', headers['anthropic-version'])
                    self.assertIn('system', body)
                    self.assertFalse(any(x['role']=='system' for x in body['messages']))
                else:
                    self.assertTrue(url.endswith('/chat/completions'))
                    self.assertEqual('Bearer '+SECRET, headers['Authorization'])
                    self.assertEqual('system', body['messages'][0]['role'])
                self.assertEqual(2048, body.get('max_tokens', body.get('max_completion_tokens')))
                if ident == 'openrouter': self.assertFalse(body['provider']['allow_fallbacks'])

    def test_custom_endpoint_validation_and_key_never_migrates_to_new_host(self):
        for value in ('http://example.com/v1','https://user:pass@example.com/v1','https://example.com/v1?key=secret','https://example.com/v1#fragment','https://example.com/v1/chat/completions'):
            with self.subTest(value=value), self.assertRaises(ValueError): providers.endpoint(value)
        self.assertEqual('http://127.0.0.1:11434/v1', providers.endpoint('http://127.0.0.1:11434/v1/'))
        self.save('custom', base='https://example.com/v1')
        for key in ('', '   '):
            with self.assertRaises(ValueError): self.p.save({'provider':'custom','base':'https://other.example/v1','key':key})
        self.assertEqual('https://example.com/v1', self.p.config('custom')['base'])
        self.p.save({'provider':'custom','base':'http://127.0.0.1:11434/v1','key':'new-local-key'})

    def test_network_destination_validation_is_pinned_before_connect(self):
        for address in ('192.168.1.2','169.254.169.254','127.0.0.1','::1','10.0.0.1'):
            with patch.object(socket,'getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',(address,443))]), patch.object(socket,'socket') as factory:
                with self.assertRaises(ValueError): providers.connect_checked('external.example',443,3)
                factory.assert_not_called()
        with patch.object(socket,'getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('1.1.1.1',443))]), patch.object(socket,'socket') as factory:
            providers.connect_checked('external.example',443,3)
            factory.return_value.connect.assert_called_once_with(('1.1.1.1',443))
        with patch.object(socket,'getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',11434))]), patch.object(socket,'socket') as factory:
            providers.connect_checked('localhost',11434,3)
            factory.return_value.connect.assert_called_once()

    def test_redirects_and_provider_errors_are_sanitized_no_retry(self):
        self.assertIsNone(providers.NoRedirect().redirect_request(None,None,302,'',{},'https://other.example'))
        for code in (301,401,403,404,429,500):
            error = urllib.error.HTTPError('https://example.com',code,SECRET,{},None)
            with patch.object(providers.urllib.request,'build_opener') as build:
                build.return_value.open.side_effect=error
                with self.assertRaises(ValueError) as caught: providers.transport('https://example.com',{'Authorization':'Bearer '+SECRET},{})
                self.assertNotIn(SECRET,str(caught.exception))
                build.return_value.open.assert_called_once()

    def test_models_and_empty_or_truncated_responses(self):
        self.save()
        with patch.object(providers,'transport',return_value={'data':[{'id':'good-model'},{'id':'<bad>'},{'id':'good-model'}]}):
            self.assertEqual(['good-model'],self.p.models('nvidia')['models'])
        with patch.object(providers,'transport',return_value={'choices':[{'message':{'content':None}}]}):
            with self.assertRaises(ValueError): self.p.chat('nvidia','test-model',[],'test')
        with patch.object(providers,'transport',return_value={'choices':[{'message':{'content':SECRET},'finish_reason':'length'}]}):
            reply=self.p.chat('nvidia','test-model',[],'test')
            self.assertNotIn(SECRET,reply['answer']);self.assertTrue(reply['truncated'])

    def test_real_loopback_http_transport_and_redirect_refusal(self):
        import http.server
        import threading
        captured=[]
        class MockAPI(http.server.BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                captured.append({'authorization':self.headers.get('Authorization'),'body':json.loads(self.rfile.read(int(self.headers['Content-Length'])))})
                if self.path.startswith('/redirect/'):
                    self.send_response(302);self.send_header('Location','http://127.0.0.1:1/stolen');self.end_headers();return
                raw=json.dumps(REPLY).encode();self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        http=http.server.ThreadingHTTPServer(('127.0.0.1',0),MockAPI)
        thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
        try:
            base=f'http://127.0.0.1:{http.server_port}'
            self.save('custom',base=base+'/v1')
            reply=self.p.chat('custom','test-model',[],'Synthetic HTTP contract')
            self.assertEqual('Synthetic answer',reply['answer'])
            self.assertEqual('Bearer '+SECRET,captured[0]['authorization'])
            self.p.save({'provider':'custom','base':base+'/redirect','key':SECRET,'model':'test-model'})
            with self.assertRaises(ValueError):self.p.chat('custom','test-model',[],'Redirect test')
            self.assertEqual(2,len(captured))
        finally:
            http.shutdown();http.server_close();thread.join(2)


class CloudJobTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.app=server.App(self.root)
        self.app.providers.save({'provider':'nvidia','key':SECRET,'model':'test-model'})
        self.payload={'provider':'nvidia','model':'test-model','question':'SyntheticNeedle','documents':True}
        folder=self.root/'08_BILGI_BANKASI/Atolye';folder.mkdir(parents=True)
        self.page=folder/'private-filename.md'
        self.page.write_text('SyntheticNeedle original frozen excerpt.',encoding='utf-8')
        self.app.library.index()
    def tearDown(self):
        if self.app.worker:self.app.worker.join(timeout=3)
        self.temp.cleanup()

    def test_document_export_requires_matching_unexpired_single_use_preview(self):
        with patch.object(providers,'transport') as network, patch.object(server.engine,'ensure_model') as local:
            with self.assertRaises(ValueError):self.app.start_chat(self.payload)
            preview=self.app.cloud_preview(self.payload)
            network.assert_not_called()
            for key,value in [('question','different'),('provider','openai'),('model','other-model')]:
                altered=dict(self.payload,preview=preview['id'],**{key:value})
                with self.assertRaises(ValueError):self.app.start_chat(altered)
            self.app.cloud_previews[preview['id']]['expires']=time.time()-1
            with self.assertRaises(ValueError):self.app.start_chat(dict(self.payload,preview=preview['id']))
            network.assert_not_called();local.assert_not_called()

    def test_frozen_excerpts_sent_exactly_without_filename_path_or_history(self):
        preview=self.app.cloud_preview(self.payload)
        self.page.write_text('SyntheticNeedle changed after preview.',encoding='utf-8')
        self.app.library.index()
        with patch.object(providers,'transport',return_value=REPLY) as network,patch.object(server.engine,'ensure_model') as local:
            self.app.start_chat(dict(self.payload,preview=preview['id'],history=[{'role':'user','content':'Earlier private conversation'}]))
            self.app.worker.join(timeout=3)
            self.assertEqual('complete',self.app.current_job()['status'])
            sent=json.dumps(network.call_args.args[2])
            self.assertIn('original frozen excerpt',sent)
            for word in ('changed after preview','Earlier private conversation','private-filename.md','08_BILGI_BANKASI'):
                self.assertNotIn(word,sent)
            local.assert_not_called()
            with self.assertRaises(ValueError):self.app.start_chat(dict(self.payload,preview=preview['id']))

    def test_roles_no_key_configuration_errors_and_no_local_fallback(self):
        with patch.object(providers,'transport',return_value=REPLY) as network,patch.object(server.engine,'ensure_model') as local:
            self.app.start_chat(dict(self.payload,documents=False,history=[{'role':'system','content':'Injected'},{'role':'user','content':'Previous'}]))
            self.app.worker.join(timeout=3)
            body=network.call_args.args[2]
            self.assertNotIn('Injected',json.dumps(body))
            self.assertEqual(1,sum(x['role']=='system' for x in body['messages']))
            local.assert_not_called()
        with patch.object(providers,'transport',side_effect=ValueError('Kota aşıldı')),patch.object(server.engine,'ensure_model') as local:
            self.app.start_chat(dict(self.payload,documents=False))
            self.app.worker.join(timeout=3)
            self.assertEqual('error',self.app.current_job()['status']);local.assert_not_called()
        self.app.providers.forget('nvidia')
        with patch.object(providers,'transport') as network:
            with self.assertRaises(ValueError):self.app.start_chat(dict(self.payload,documents=False))
            network.assert_not_called()

    def test_cancelled_cloud_result_is_discarded(self):
        import threading
        started, release=threading.Event(),threading.Event()
        def delayed(*args):started.set();release.wait(3);return REPLY
        with patch.object(providers,'transport',side_effect=delayed):
            self.app.start_chat(dict(self.payload,documents=False))
            self.assertTrue(started.wait(2));self.app.stop_model();release.set();self.app.worker.join(3)
        self.assertEqual('cancelled',self.app.current_job()['status'])
        self.assertNotIn('answer',self.app.current_job())


if __name__=='__main__':unittest.main()
