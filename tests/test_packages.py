"""Package integrity, extraction, cancellation, and HTTP authorization checks."""
import hashlib
import io
import json
from pathlib import Path
import stat
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import engine
import packages
import package_lifecycle
import server


def archive(entries=None):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        for name,content in (entries or {'nested/app.exe':b'MZsynthetic executable'}).items():z.writestr(name,content)
    return stream.getvalue()


class Response(io.BytesIO):
    status=200
    def __init__(self,content):
        super().__init__(content);self.headers={'Content-Length':str(len(content))}


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.catalog=self.root/'catalog.json'
        self.payload=archive()
        self.row={'id':'sample','name':'Sample','category':'Test','description':'Fixture',
            'version':'1.0','kind':'zip','entry':'app.exe','url':'https://example.com/sample.zip',
            'sha256':hashlib.sha256(self.payload).hexdigest(),'bytes':len(self.payload),
            'verification':'publisher-sha256-match','existing_folder':'01_TASINABILIR/Sample'}
    def tearDown(self):self.temp.cleanup()
    def manager(self,rows=None):
        self.catalog.write_text(json.dumps({'packages':rows or [self.row]}),encoding='utf-8')
        return packages.Packages(self.root,self.catalog)
    def run_queue(self,manager,ids=None,payload=None):
        with patch('packages.open_download',side_effect=lambda _:Response(payload or self.payload)) as download,patch('packages.subprocess.Popen') as launch:
            manager.start(ids or ['sample']);manager.worker.join(5)
            self.assertFalse(manager.worker.is_alive());launch.assert_not_called()
            return manager.current(),download.call_count
    def test_shipped_catalog_is_complete_offline_and_classified(self):
        with patch('packages.open_download') as network:
            manager=packages.Packages(self.root);rows=manager.snapshot()['packages']
            self.assertEqual(30,len(rows));self.assertEqual(25,sum(x['kind']!='installer' for x in rows))
            self.assertEqual(5,sum(x['kind']=='installer' for x in rows))
            self.assertFalse(any(x['ready'] for x in rows));self.assertEqual([],manager.entries());network.assert_not_called()
    def test_download_verify_prepare_receipt_menu_restart_and_no_execution(self):
        manager=self.manager();job,calls=self.run_queue(manager,['sample','sample'])
        self.assertEqual(('complete',1,1),(job['status'],job['total'],calls))
        self.assertEqual('complete',job['items'][0]['state'])
        entry=manager.entries()[0];self.assertEqual('package-sample',entry['id'])
        self.assertEqual(b'MZsynthetic executable',Path(entry['path']).read_bytes())
        restarted=self.manager();self.assertTrue(restarted.snapshot()['packages'][0]['ready'])
        job,calls=self.run_queue(restarted);self.assertEqual('skipped',job['items'][0]['state']);self.assertEqual(0,calls)
        with patch.object(engine,'ROOT',self.root):self.assertEqual(Path(entry['path']),engine.find_file(self.row['existing_folder'],'app.exe'))
    def test_installer_downloads_without_execution_and_detects_changes(self):
        data=b'MZ installer fixture';row=dict(self.row,id='installer',kind='installer',url='https://example.com/setup.exe',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        manager=self.manager([row]);job,_=self.run_queue(manager,['installer'],data)
        self.assertEqual('complete',job['status']);self.assertEqual('folder',manager.entries()[0]['type'])
        file=self.root/manager.receipts['installer']['entry'];file.write_bytes(b'changed')
        self.assertFalse(manager.snapshot()['packages'][0]['ready'])
        manager.remove_package('installer')
        with self.assertRaises(ValueError):manager.restore_package(manager.removed()[0]['id'])
        self.assertEqual([],manager.entries());self.assertTrue(manager.removed())
    def test_valid_cached_archive_works_without_network(self):
        self.row['existing_archive']='02_KURULUMLAR/original.zip'
        cached=self.root/self.row['existing_archive'];cached.parent.mkdir();cached.write_bytes(self.payload)
        manager=self.manager();job,calls=self.run_queue(manager)
        self.assertEqual(('complete',0),(job['status'],calls));self.assertEqual(self.payload,cached.read_bytes())
    def test_existing_program_is_preserved_and_not_downloaded(self):
        exe=self.root/self.row['existing_folder']/'app.exe';exe.parent.mkdir(parents=True);exe.write_bytes(b'existing version')
        manager=self.manager();job,calls=self.run_queue(manager)
        self.assertEqual(('skipped',0),(job['items'][0]['state'],calls))
        self.assertEqual(b'existing version',exe.read_bytes());self.assertFalse(manager.snapshot()['packages'][0]['managed'])
    def test_bad_hash_or_truncated_download_leaves_no_partial_or_program(self):
        for data in (self.payload[:-1],b'x'*len(self.payload)):
            manager=self.manager();job,_=self.run_queue(manager,payload=data)
            self.assertEqual('error',job['items'][0]['state'])
            self.assertEqual([],list(self.root.rglob('*.part')));self.assertEqual([],manager.entries())
    def test_zip_rejects_traversal_ads_reserved_names_collision_and_symlinks(self):
        for name in ('../escaped.exe','/abs.exe','C:/abs.exe','safe/file:ads','CON.txt','bad./app.exe','safe\\..\\x.exe'):
            with zipfile.ZipFile(io.BytesIO(archive({name:b'x'}))) as z:
                with self.assertRaises(ValueError,msg=name):packages.zip_plan(z)
        with zipfile.ZipFile(io.BytesIO(archive({'App.exe':b'MZ','app.exe':b'MZ'}))) as z:
            with self.assertRaises(ValueError):packages.zip_plan(z)
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            item=zipfile.ZipInfo('link');item.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(item,'../outside')
        with zipfile.ZipFile(io.BytesIO(stream.getvalue())) as z:
            with self.assertRaises(ValueError):packages.zip_plan(z)
    def test_unsafe_archive_is_cleaned_and_remaining_package_continues(self):
        bad=archive({'../escape.exe':b'MZ'});badrow=dict(self.row,id='bad',bytes=len(bad),sha256=hashlib.sha256(bad).hexdigest())
        manager=self.manager([badrow,self.row])
        with patch('packages.open_download',side_effect=[Response(bad),Response(self.payload)]):
            manager.start(['bad','sample']);manager.worker.join(5)
        self.assertEqual(['error','complete'],[x['state'] for x in manager.current()['items']])
        self.assertEqual([],list(self.root.rglob('.hazirlama-*')));self.assertFalse((self.root.parent/'escape.exe').exists())
    def test_cancel_cleans_part_skips_remaining_and_blocks_root_change(self):
        manager=self.manager([self.row,dict(self.row,id='second')]);started=threading.Event();release=threading.Event()
        class Blocking(Response):
            def read(self,*args):started.set();release.wait(5);return super().read(*args)
        with patch('packages.open_download',return_value=Blocking(self.payload)):
            manager.start(['sample','second']);self.assertTrue(started.wait(3))
            with self.assertRaises(ValueError):manager.start(['sample'])
            app=server.App(self.root);app.package_manager=manager
            with self.assertRaises(ValueError):app.setup_apply({'root':str(self.root)})
            manager.cancel_current();release.set();manager.worker.join(5)
        self.assertEqual('cancelled',manager.current()['status'])
        self.assertEqual(['cancelled','cancelled'],[x['state'] for x in manager.current()['items']])
        self.assertEqual([],list(self.root.rglob('*.part')));self.assertEqual([],manager.entries())
    def test_invalid_selection_and_receipt_cannot_escape_root(self):
        manager=self.manager()
        for ids in ([],['unknown'],'sample',[None]):
            with self.assertRaises(ValueError):manager.start(ids)
        manager.receipts={'sample':{'sha256':self.row['sha256'],'entry':'../outside.exe'}}
        self.assertFalse(manager.snapshot()['packages'][0]['ready'])
        manager.receipts={'sample':[]};self.assertFalse(manager.snapshot()['packages'][0]['ready'])
    def test_receipt_write_failure_rolls_back_only_own_folder_and_can_retry(self):
        manager=self.manager()
        with patch('packages.write_json',side_effect=OSError('synthetic disk failure')):
            job,_=self.run_queue(manager)
        self.assertEqual('partial',job['status']);self.assertEqual([],list((self.root/'01_TASINABILIR/PaketMerkezi').iterdir()))
        job,calls=self.run_queue(manager);self.assertEqual(('complete',0),(job['status'],calls))

    def test_interrupted_download_resumes_after_restart_with_validated_range(self):
        manager=self.manager();payload=self.payload
        class Interrupted(Response):
            def read(self,*args):
                if self.tell():raise OSError('synthetic connection loss')
                return super().read(40)
        with patch('packages.open_download',return_value=Interrupted(payload)):
            manager.start(['sample']);manager.worker.join(5)
        partial=manager.partial_path(self.row);self.assertEqual(payload[:40],partial.read_bytes())
        restarted=self.manager();self.assertEqual(40,restarted.snapshot()['packages'][0]['partial_bytes'])
        response=Response(payload[40:]);response.status=206;response.headers['Content-Range']=f'bytes 40-{len(payload)-1}/{len(payload)}'
        with patch('packages.open_download',return_value=response) as request:
            restarted.start(['sample']);restarted.worker.join(5)
        request.assert_called_once_with(self.row['url'],40)
        self.assertEqual('complete',restarted.current()['status']);self.assertFalse(partial.exists())
    def test_server_ignoring_range_restarts_without_appending(self):
        manager=self.manager();part=manager.partial_path(self.row);part.parent.mkdir(parents=True);part.write_bytes(self.payload[:20])
        with patch('packages.open_download',return_value=Response(self.payload)):
            manager.start(['sample']);manager.worker.join(5)
        self.assertEqual('complete',manager.current()['status']);self.assertEqual(b'MZsynthetic executable',Path(manager.entries()[0]['path']).read_bytes())
    def test_cancel_after_progress_keeps_prefix_and_never_starts_next_package(self):
        manager=self.manager([self.row,dict(self.row,id='second')]);payload=self.payload
        class CancelAfterPrefix(Response):
            def read(self,*args):
                if self.tell():manager.cancel_current()
                return super().read(40)
        with patch('packages.open_download',return_value=CancelAfterPrefix(payload)) as network:
            manager.start(['sample','second']);manager.worker.join(5)
        self.assertEqual(1,network.call_count);self.assertEqual(payload[:40],manager.partial_path(self.row).read_bytes())
        self.assertEqual('cancelled',manager.current()['status']);self.assertEqual([],manager.entries())
    def test_invalid_range_preserves_prefix_and_corrupt_prefix_never_prepares(self):
        manager=self.manager();part=manager.partial_path(self.row);part.parent.mkdir(parents=True);part.write_bytes(self.payload[:20])
        response=Response(self.payload[20:]);response.status=206;response.headers['Content-Range']='bytes 0-10/11'
        with patch('packages.open_download',return_value=response):manager.start(['sample']);manager.worker.join(5)
        self.assertEqual(self.payload[:20],part.read_bytes());self.assertEqual([],manager.entries())
        part.write_bytes(b'x'*20);response=Response(self.payload[20:]);response.status=206;response.headers['Content-Range']=f'bytes 20-{len(self.payload)-1}/{len(self.payload)}'
        with patch('packages.open_download',return_value=response):manager.start(['sample']);manager.worker.join(5)
        self.assertFalse(part.exists());self.assertEqual('error',manager.current()['items'][0]['state'])
    def test_remove_restore_preserves_program_data_and_original_files(self):
        manager=self.manager();self.run_queue(manager)
        entry=Path(manager.entries()[0]['path']);user_data=entry.parent/'notes.txt';user_data.write_text('my data')
        manager.remove_package('sample');self.assertFalse(entry.exists());self.assertEqual([],manager.entries())
        removal=manager.removed()[0]['id'];self.assertEqual('sample',manager.removed()[0]['package'])
        restarted=self.manager();restarted.restore_package(removal)
        self.assertEqual('my data',user_data.read_text());self.assertTrue(entry.exists());self.assertEqual([],restarted.removed())
    def test_remove_only_managed_and_blocks_running_app(self):
        manager=self.manager()
        with self.assertRaises(ValueError):manager.remove_package('sample')
        self.run_queue(manager)
        class Running:
            def poll(self):return None
        manager.launched['package-sample']=Running()
        with self.assertRaises(ValueError):manager.remove_package('sample')
        self.assertTrue(Path(manager.entries()[0]['path']).is_file())
        with self.assertRaises(ValueError):manager.restore_package('../escape')
    def test_restore_will_not_overwrite_new_copy_and_remove_write_error_rolls_back(self):
        manager=self.manager();self.run_queue(manager);entry=Path(manager.entries()[0]['path'])
        with patch('package_lifecycle.write_json',side_effect=[None,OSError('disk error'),None]):
            with self.assertRaises(ValueError):manager.remove_package('sample')
        self.assertTrue(entry.exists());self.assertTrue(manager.locate(self.row)[1])
        manager.remove_package('sample');removal=manager.removed()[0]['id']
        entry.parent.mkdir(parents=True);entry.write_bytes(b'new copy')
        with self.assertRaises(ValueError):manager.restore_package(removal)
        self.assertEqual(b'new copy',entry.read_bytes());self.assertTrue(manager.removed())
    def test_update_checks_classify_versions_errors_and_manual_without_install(self):
        row=dict(self.row,url='https://github.com/official/project/releases/download/v1.0/file.zip')
        for version,status in (('v1.0','current'),('v2.0','available'),('v0.9','catalog_ahead')):
            with patch('package_lifecycle.fetch_json',return_value={'tag_name':version}):
                self.assertEqual(status,package_lifecycle.check_publisher(row)['status'])
        with patch('package_lifecycle.fetch_json',side_effect=OSError()):self.assertEqual('error',package_lifecycle.check_publisher(row)['status'])
        with patch('package_lifecycle.fetch_json') as fetch:
            self.assertEqual('manual',package_lifecycle.check_publisher(dict(row,id='python-installer'))['status']);fetch.assert_not_called()
        manager=self.manager([row])
        with patch('package_lifecycle.fetch_json',return_value={'tag_name':'v2.0'}) as fetch,patch('packages.open_download') as download:
            manager.check_updates();manager.update_worker.join(5);manager.check_updates()
            self.assertEqual(1,fetch.call_count);download.assert_not_called()
        self.assertEqual('complete',manager.updates['status']);self.assertFalse(manager.entries())
    def test_vendor_metadata_stable_channels(self):
        for ident,response,expected in (
            ('vscode',{'productVersion':'2.0'},'2.0'),
            ('node',[{'version':'v99.0','lts':False},{'version':'v24.22.0','lts':'Krypton'}],'v24.22.0'),
            ('dotnet',{'releases-index':[{'support-phase':'active','latest-sdk':'10.0.402'},{'support-phase':'preview','latest-sdk':'11.0.100-preview'}]},'10.0.402')):
            with patch('package_lifecycle.fetch_json',return_value=response):
                result=package_lifecycle.check_publisher(dict(self.row,id=ident));self.assertEqual(expected,result['latest'])
    def test_long_windows_path_is_reported_before_extraction(self):
        payload=archive({'app.exe':b'MZtest','nested/'+'x'*220+'.txt':b'data'})
        row=dict(self.row,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())
        manager=self.manager([row])
        with patch('packages.os.name','nt'):
            job,_=self.run_queue(manager,payload=payload)
        self.assertEqual('partial',job['status']);self.assertIn('çok uzun',job['items'][0]['message'])
        self.assertEqual([],manager.entries());self.assertTrue(list(self.root.rglob('*.zip')))


if __name__=='__main__':unittest.main()
