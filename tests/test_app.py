"""Behavior checks use an empty temporary kit, never a user's real files."""
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
import http.server

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
import server


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config_patch = patch.object(server, 'LOCAL_CONFIG', self.root / 'bootstrap.json')
        self.config_patch.start()
        self.app = server.App(self.root)
        self.http = http.server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        self.http.app = self.app
        self.app.port = self.http.server_port
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.temp.cleanup()
        self.config_patch.stop()

    def request(self, path, data=None, token=True, origin=None, host=None, raw=None):
        headers = {}
        if data is not None or raw is not None:
            headers['Content-Type'] = 'application/json'
            if token:
                headers['X-Atolye-Token'] = self.app.token
        if origin:
            headers['Origin'] = origin
        if host:
            headers['Host'] = host
        body = raw if raw is not None else json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(f'http://127.0.0.1:{self.app.port}{path}', data=body, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read()
                return response.status, json.loads(content) if response.headers['Content-Type'].startswith('application/json') else content
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    def test_mutations_require_token_and_same_origin(self):
        self.assertEqual(403, self.request('/api/favorites', {'favorites': []}, token=False)[0])
        self.assertEqual(403, self.request('/api/favorites', {'favorites': []}, origin='https://example.org')[0])
        self.assertEqual(403, self.request('/api/state', host='evil.example')[0])
        self.assertEqual(400, self.request('/api/favorites', raw=b'[]')[0])
        self.assertEqual(200, self.request('/api/favorites', {'favorites': ['vscode', 'untrusted']})[0])
        prefs = json.loads((self.app.logs / 'app-tercihler.json').read_text())
        self.assertEqual(['vscode'], prefs['favorites'])

    def test_provider_routes_do_not_expose_keys_and_need_mutation_token(self):
        secret='synthetic-http-key-not-real'
        data={'provider':'nvidia','key':secret,'model':'test-model'}
        self.assertEqual(403,self.request('/api/providers/save',data,token=False)[0])
        self.assertEqual(200,self.request('/api/providers/save',data)[0])
        self.assertNotIn(secret,json.dumps(self.request('/api/state')[1]))
        self.assertEqual(200,self.request('/providers.js')[0])
        with patch('providers.transport',return_value={'choices':[{'message':{'content':'OK'}}]}):
            self.assertEqual(200,self.request('/api/providers/test',{'provider':'nvidia','model':'test-model'})[0])
        self.assertEqual(200,self.request('/api/providers/forget',{'provider':'nvidia'})[0])
        self.assertEqual(400,self.request('/api/chat',{'question':'Hello','provider':'nvidia','model':'test-model'})[0])

    def test_outside_paths_and_unknown_programs_are_rejected(self):
        with self.assertRaises(ValueError):
            server.safe_path(self.root, '../private.txt')
        with patch.object(server.os, 'startfile') as start:
            self.assertEqual(400, self.request('/api/open', {'id': 'powershell.exe'})[0])
            self.assertEqual(400, self.request('/api/project/open', {'id': '../'})[0])
            self.assertEqual(400, self.request('/api/library/open', {'path': '../private.txt'})[0])
            start.assert_not_called()
        rows = [{'id': 'escape', 'path': '../private.txt', 'url': 'https://private?secret=1', 'status': 'downloaded'}]
        (self.root / '00_BASLANGIC/paketler.json').write_text(json.dumps(rows))
        package = self.app.packages()[0]
        self.assertFalse(package['ready'])
        self.assertNotIn('url', package)

    def test_catalog_http_is_offline_and_download_mutations_require_authorization(self):
        with patch('packages.open_download') as network:
            code,result=self.request('/api/catalog')
            self.assertEqual(200,code);self.assertEqual(30,len(result['packages']))
            self.assertEqual(403,self.request('/api/catalog/install',{'ids':['peazip']},token=False)[0])
            self.assertEqual(403,self.request('/api/catalog/install',{'ids':['peazip']},origin='https://evil.example')[0])
            for route in ('updates','remove','restore'):
                self.assertEqual(403,self.request('/api/catalog/'+route,{'id':'peazip'},token=False)[0])
            self.assertEqual(400,self.request('/api/catalog/remove',{'id':'vscode'})[0])
            self.assertEqual(400,self.request('/api/catalog/restore',{'id':'../outside'})[0])
            self.assertEqual(400,self.request('/api/catalog/install',{'ids':['../unlisted']})[0])
            self.assertEqual(200,self.request('/api/catalog/job')[0])
            self.assertEqual(200,self.request('/catalog.js')[0]);self.assertEqual(200,self.request('/catalog.css')[0])
            network.assert_not_called()

    def test_incremental_search_and_deletion(self):
        folder = self.root / '08_BILGI_BANKASI/Atolye'
        folder.mkdir(parents=True)
        page = folder / 'Guide.md'
        page.write_text('UniqueAlpha: start the workshop with BASLAT.cmd.', encoding='utf-8')
        (folder / '.env').write_text('PRIVATE_PASSWORD=SecretNeedle')
        self.app.library.index()
        self.assertEqual(1, self.app.library.status()['files'])
        self.assertTrue(self.app.library.search('UniqueAlpha'))
        self.assertFalse(self.app.library.search('SecretNeedle'))
        page.write_text('UniqueBeta: use the new launcher.', encoding='utf-8')
        self.app.library.index()
        self.assertFalse(self.app.library.search('UniqueAlpha'))
        self.assertTrue(self.app.library.search('UniqueBeta'))
        page.unlink()
        self.app.library.index()
        self.assertEqual(0, self.app.library.status()['files'])

    def test_job_no_source_never_launches_model(self):
        with patch.object(server.engine, 'ensure_model') as launch:
            self.app.start_chat({'question': 'Unknown', 'documents': True, 'model': 'gemma-e2b'})
            self.app.worker.join(timeout=3)
            self.assertEqual('complete', self.app.current_job()['status'])
            launch.assert_not_called()

    def test_job_exclusivity_cancellation_and_cleaning(self):
        with patch.object(server.engine, 'ensure_model'), patch.object(server.engine, 'model_healthy', return_value=False):
            self.app.start_chat({'question': 'Hello', 'model': 'gemma-e2b'})
            with self.assertRaises(ValueError):
                self.app.start_chat({'question': 'Duplicate'})
            self.app.stop_model()
            self.app.worker.join(timeout=3)
            self.assertEqual('cancelled', self.app.current_job()['status'])
            self.app.action('/api/chat/clear', {})
            self.assertIsNone(self.app.current_job())

    def test_normal_chat_uses_only_validated_recent_roles(self):
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, *args): return b'{"choices":[{"message":{"content":"A local reply"}}]}'
        with patch.object(server.engine, 'ensure_model'), patch.object(server.engine, 'model_healthy', return_value=True), patch.object(server.urllib.request, 'urlopen', return_value=Reply()) as call:
            self.app.start_chat({'question': 'Hello', 'history': [{'role':'system','content':'untrusted override'}, {'role':'user','content':'Previous question'}]})
            self.app.worker.join(timeout=3)
            self.assertEqual('complete', self.app.current_job()['status'])
            self.assertEqual('A local reply', self.app.current_job()['answer'])
            sent = json.loads(call.call_args.args[0].data)
            self.assertEqual(1, sum(x['role']=='system' for x in sent['messages']))
            self.assertNotIn('untrusted override', str(sent))
            self.assertEqual('Bearer ' + server.engine.MODEL_KEY, call.call_args.args[0].get_header('Authorization'))
            self.assertEqual('http://127.0.0.1:8086/v1/chat/completions', call.call_args.args[0].full_url)

    def test_interface_language_is_validated_persistent_and_offline(self):
        with patch.object(server.urllib.request, 'urlopen') as external:
            self.assertEqual({'language': 'en'}, self.app.preferences())
            self.app.action('/api/preferences', {'language': 'tr', 'extra': 'discard'})
            self.assertEqual({'language': 'tr'}, server.App(self.root).preferences())
            with self.assertRaises(ValueError):
                self.app.action('/api/preferences', {'language': 'unknown'})
            external.assert_not_called()
        self.assertEqual(403, self.request('/api/preferences', {'language': 'en'}, token=False)[0])
        self.assertEqual(400, self.request('/api/preferences', {'language': 'de'})[0])
        self.assertEqual(200, self.request('/i18n.js')[0])

    def test_general_chat_needs_no_documents_and_preserves_recent_context(self):
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, *args): return b'{"choices":[{"message":{"content":"Hello again"},"finish_reason":"length"}]}'
        history = [{'role': 'user', 'content': 'My name is Deniz.'}, {'role': 'assistant', 'content': 'Hello Deniz.'}]
        with patch.object(server.engine, 'ensure_model'), patch.object(server.engine, 'model_healthy', return_value=True), patch.object(self.app.library, 'search', side_effect=AssertionError('General chat must not search documents')), patch.object(server.urllib.request, 'urlopen', return_value=Reply()) as call:
            self.app.start_chat({'question': 'What is my name?', 'history': history, 'documents': False})
            self.app.worker.join(timeout=3)
            job = self.app.current_job()
            self.assertEqual('complete', job['status'])
            self.assertEqual([], job['sources'])
            self.assertTrue(job['truncated'])
            sent = json.loads(call.call_args.args[0].data)
            self.assertEqual(history, sent['messages'][1:-1])
            self.assertIn('language of the latest user message', sent['messages'][0]['content'])

    def test_empty_local_reply_is_an_error(self):
        class Reply:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, *args): return b'{"choices":[{"message":{"content":""}}]}'
        with patch.object(server.engine, 'ensure_model'), patch.object(server.engine, 'model_healthy', return_value=True), patch.object(server.urllib.request, 'urlopen', return_value=Reply()):
            self.app.start_chat({'question': 'Hello'})
            self.app.worker.join(timeout=3)
            self.assertEqual('error', self.app.current_job()['status'])

    def test_known_native_tool_launches_as_an_argument_list(self):
        folder = self.root / '01_TASINABILIR/SumatraPDF'
        folder.mkdir(parents=True)
        executable = folder / 'SumatraPDF.exe'
        executable.touch()
        with patch.object(server.engine.subprocess, 'Popen') as launch:
            response = self.app.action('/api/open', {'id': 'sumatra'})
            self.assertIn('açıldı', response['message'])
            self.assertEqual([str(executable.resolve())], launch.call_args.args[0])
            self.assertNotIn('shell', launch.call_args.kwargs)


if __name__ == '__main__':
    unittest.main()
