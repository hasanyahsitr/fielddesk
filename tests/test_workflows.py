"""End-to-end workflow tests on synthetic documents and images only."""
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
if os.environ.get('ATOLYE_TEST_PACKAGES'):
    sys.path.insert(0, os.environ['ATOLYE_TEST_PACKAGES'])
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
from PIL import Image
import server
from features import CustomApps, browse, setup_preview
from workflows import Workflows, fingerprint, MAX_FILE


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.input = self.root / 'inputs'
        self.input.mkdir()
        self.project = self.root / '04_PROJELER/test %PATH% & unicode-ç'
        self.project.mkdir(parents=True)
        (self.project/'package.json').write_text(json.dumps({'scripts': {'dev': 'NEVER_EXECUTE_THIS'}}))
        self.project_row = {'id': 'project-1', 'name': self.project.name, 'path': self.project.relative_to(self.root).as_posix()}
        self.flow = Workflows(self.root, lambda: [self.project_row], lambda: None)

    def tearDown(self):
        if self.flow.worker:
            self.flow.worker.join(timeout=10)
        self.temp.cleanup()

    def pdf(self, name, widths):
        path = self.input / name
        writer = PdfWriter()
        for width in widths:
            page = writer.add_blank_page(width=width, height=600)
            font = DictionaryObject({NameObject('/Type'):NameObject('/Font'),
                                     NameObject('/Subtype'):NameObject('/Type1'),
                                     NameObject('/BaseFont'):NameObject('/Helvetica')})
            page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'):
                DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
            content = DecodedStreamObject()
            content.set_data(f'BT /F1 12 Tf 20 30 Td (page-{width}) Tj ET'.encode())
            page[NameObject('/Contents')] = writer._add_object(content)
        with path.open('wb') as f:
            writer.write(f)
        writer.close()
        return path.relative_to(self.root).as_posix()

    def execute(self, plan):
        self.flow.start(plan['id'])
        self.flow.worker.join(timeout=10)
        job = self.flow.current()
        self.assertEqual('complete', job['status'], job.get('message'))
        return job, self.root / job['output']

    def test_pdf_order_page_count_and_source_integrity(self):
        first = self.pdf('first.pdf', [310, 320])
        second = self.pdf('second.pdf', [410])
        before = [fingerprint(self.root/p) for p in [first, second]]
        plan = self.flow.preview({'kind':'pdf','files':[second,first]})
        self.assertEqual(3, plan['pages'])
        self.assertFalse((self.root/'12_ISLER/Ciktilar').exists())
        job, output = self.execute(plan)
        with (output/'birlestirilmis.pdf').open('rb') as stream:
            reader = PdfReader(stream)
            self.assertEqual([410,310,320], [int(p.mediabox.width) for p in reader.pages])
            self.assertEqual(['page-410','page-310','page-320'], [p.extract_text() for p in reader.pages])
        self.assertEqual(before, [fingerprint(self.root/p) for p in [first,second]])
        self.assertTrue(json.loads((output/'islem-raporu.json').read_text(encoding='utf-8'))['completed'])
        with self.assertRaises(ValueError):
            self.flow.start(plan['id'])

    def test_changed_input_rejects_execution_before_output(self):
        path = self.pdf('changed.pdf', [300])
        plan = self.flow.preview({'kind':'pdf','files':[path]})
        (self.root/path).write_bytes(b'changed')
        self.flow.start(plan['id'])
        self.flow.worker.join(timeout=5)
        self.assertEqual('error', self.flow.current()['status'])
        self.assertFalse((self.root/'12_ISLER/Ciktilar').exists())

    def test_encrypted_and_outside_inputs_rejected(self):
        writer = PdfWriter()
        writer.add_blank_page(width=300, height=300)
        writer.encrypt('secret')
        path = self.input/'encrypted.pdf'
        with path.open('wb') as f:
            writer.write(f)
        writer.close()
        with self.assertRaisesRegex(ValueError, 'şifreli'):
            self.flow.preview({'kind':'pdf','files':['inputs/encrypted.pdf']})
        with self.assertRaises(ValueError):
            self.flow.preview({'kind':'pdf','files':['../outside.pdf']})

    def test_images_resize_alpha_exif_and_no_upscale(self):
        image = Image.new('RGBA', (1600,800), (200,30,60,0))
        image.save(self.input/'alpha.png')
        small = Image.new('RGB', (200,100), 'blue')
        exif = Image.Exif()
        exif[270] = 'PRIVATE-IMAGE-DESCRIPTION'
        small.save(self.input/'small.jpg', exif=exif)
        source_hash = fingerprint(self.input/'alpha.png')
        plan = self.flow.preview({'kind':'images','files':['inputs/alpha.png','inputs/small.jpg'],
                                  'options':{'width':800,'format':'webp','quality':82}})
        job, output = self.execute(plan)
        with Image.open(output/job['results'][0]['name']) as result:
            self.assertEqual((800,400), result.size)
            self.assertEqual(0,result.convert('RGBA').getpixel((0,0))[3])
        with Image.open(output/job['results'][1]['name']) as result:
            self.assertEqual((200,100),result.size)
            self.assertNotIn(270,result.getexif())
        self.assertEqual(source_hash,fingerprint(self.input/'alpha.png'))
        next_plan = self.flow.preview({'kind':'images','files':['inputs/alpha.png'],
                                       'options':{'width':800,'format':'jpeg','quality':95}})
        next_job, next_output = self.execute(next_plan)
        self.assertNotEqual(output,next_output)
        with Image.open(next_output/next_job['results'][0]['name']) as result:
            self.assertEqual((255,255,255),result.getpixel((0,0)))

    def test_upload_quota_partial_cleanup_and_extension(self):
        result = self.flow.register_upload('a.pdf',io.BytesIO(b'%PDF-test'),9)
        self.assertTrue((self.root/result['path']).is_file())
        with self.assertRaises(ValueError):
            self.flow.register_upload('broken.pdf',io.BytesIO(b'xx'),5)
        self.assertFalse(list((self.root/'12_ISLER/Girdiler').rglob('*.part')))
        with self.assertRaises(ValueError):
            self.flow.register_upload('bad.exe',io.BytesIO(b'MZ'),2)
        with self.assertRaises(ValueError):
            self.flow.register_upload('big.pdf',io.BytesIO(),MAX_FILE+1)

    def test_project_prepares_terminal_without_running_project_scripts(self):
        node = self.root/'01_TASINABILIR/Node'
        node.mkdir(parents=True)
        (node/'node.exe').write_bytes(b'MZ')
        plan = self.flow.preview({'kind':'project','project':'project-1','editor':False})
        self.assertEqual(['dev'],plan['scripts'])
        with patch.object(os,'startfile') as start, patch('subprocess.Popen') as process:
            job, output = self.execute(plan)
            start.assert_called_once_with(str(output/'proje-terminali.cmd'))
            process.assert_not_called()
        script = (output/'proje-terminali.cmd').read_text(encoding='utf-8')
        self.assertIn('%%PATH%% & unicode-ç',script)
        self.assertIn('setlocal DisableDelayedExpansion',script)
        self.assertNotIn('NEVER_EXECUTE_THIS',script)


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name).resolve()
        folder=self.root/'01_TASINABILIR/Example'
        folder.mkdir(parents=True)
        self.exe=folder/'example.exe'
        self.exe.write_bytes(b'MZ\x00\x00')
        self.apps=CustomApps(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_app_register_launch_relocate_and_remove_preserves_binary(self):
        row=self.apps.add({'name':'Example','relative':self.exe.relative_to(self.root).as_posix()})
        with patch('subprocess.Popen') as run:
            self.apps.launch(row['id'])
            self.assertEqual([str(self.exe)],run.call_args.args[0])
        with self.assertRaises(ValueError):
            self.apps.add({'name':'Duplicate','relative':row['relative']})
        relocated=self.root/'relocated'
        relocated.mkdir()
        import shutil
        shutil.copytree(self.root/'01_TASINABILIR',relocated/'01_TASINABILIR')
        shutil.copytree(self.root/'00_BASLANGIC',relocated/'00_BASLANGIC')
        self.assertTrue(CustomApps(relocated).entries()[0]['ready'])
        self.apps.remove(row['id'])
        self.assertTrue(self.exe.exists())
        self.assertFalse(self.apps.entries())

    def test_root_setup_non_destructive_and_persisted(self):
        keep=self.root/'existing.txt'
        keep.write_text('keep me')
        preview=setup_preview(self.root)
        self.assertFalse(all(x['exists'] for x in preview['folders']))
        app=server.App(self.root)
        with patch.object(server,'LOCAL_CONFIG',self.root/'bootstrap.json'):
            app.setup_apply({'root':str(self.root)})
        self.assertEqual('keep me',keep.read_text())
        self.assertTrue((self.root/'12_ISLER/Ciktilar').is_dir())
        self.assertTrue(json.loads((app.logs/'hazirlik.json').read_text())['completed'])
        self.assertTrue((self.root/'bootstrap.json').exists())
        with self.assertRaises(ValueError):
            browse(self.root,'../','apps')


if __name__ == '__main__':
    unittest.main()
