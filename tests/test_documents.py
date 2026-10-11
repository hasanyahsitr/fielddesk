import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
if os.environ.get('ATOLYE_TEST_PACKAGES'):sys.path.insert(0,os.environ['ATOLYE_TEST_PACKAGES'])
from documents import office_text
from library import Library
import ocr
from workflows import Workflows,fingerprint
from PIL import Image,ImageDraw,ImageFont
from pypdf import PdfReader


class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.folder=self.root/'04_PROJELER/Belgeler';self.folder.mkdir(parents=True)
    def tearDown(self):self.temp.cleanup()
    def package(self,name,entries):
        path=self.folder/name
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
            for key,value in entries.items():archive.writestr(key,value)
        return path
    def test_docx_text_tables_and_headers_indexed(self):
        path=self.package('teklif.docx',{'word/document.xml':'<document><p><r><t>İstanbul sözleşme</t></r><r><t> revizyonu</t></r></p><tbl><tr><tc><p><t>Bütçe 12500</t></p></tc></tr></tbl></document>',
                                      'word/header1.xml':'<hdr><p><t>AEONAVIS</t></p></hdr>',
                                      'word/_rels/document.xml.rels':'<Relationships><Relationship Target="https://example.invalid/private" TargetMode="External"/></Relationships>'})
        self.assertIn('İstanbul sözleşme revizyonu',office_text(path))
        self.assertIn('Bütçe 12500',office_text(path))
        self.assertIn('AEONAVIS',office_text(path))
        library=Library(self.root);library.index()
        self.assertEqual('04_PROJELER/Belgeler/teklif.docx',library.search('sözleşme')[0]['path'])
        path.write_bytes(b'corrupted Office file')
        library.index()
        self.assertFalse(library.search('sözleşme'))
        self.assertTrue(library.status()['errors'])
    def test_xlsx_shared_inline_cached_formula_and_sheet_order(self):
        path=self.package('tablo.xlsx',{'xl/workbook.xml':'<workbook xmlns:r="r"><sheets><sheet name="İzmir" r:id="r2"/><sheet name="Ankara" r:id="r1"/></sheets></workbook>',
            'xl/_rels/workbook.xml.rels':'<Relationships><Relationship Id="r1" Target="worksheets/sheet1.xml"/><Relationship Id="r2" Target="/xl/worksheets/sheet2.xml"/></Relationships>',
            'xl/sharedStrings.xml':'<sst><si><t>Gelir</t></si></sst>',
            'xl/worksheets/sheet1.xml':'<worksheet><sheetData><row><c t="inlineStr"><is><t>Gider</t></is></c></row></sheetData></worksheet>',
            'xl/worksheets/sheet2.xml':'<worksheet><sheetData><row><c t="s"><v>0</v></c><c><f>UNKNOWN()</f><v>42</v></c></row></sheetData></worksheet>'})
        text=office_text(path)
        self.assertLess(text.index('İzmir'),text.index('Ankara'))
        self.assertIn('Gelir | 42',text);self.assertIn('Gider',text);self.assertNotIn('UNKNOWN',text)
    def test_pptx_presentation_order_and_external_links_ignored(self):
        path=self.package('sunum.pptx',{'ppt/presentation.xml':'<presentation xmlns:r="r"><sldIdLst><sldId r:id="b"/><sldId r:id="external"/><sldId r:id="a"/></sldIdLst></presentation>',
            'ppt/_rels/presentation.xml.rels':'<Relationships><Relationship Id="a" Target="slides/slide1.xml"/><Relationship Id="b" Target="slides/slide2.xml"/><Relationship Id="external" Target="https://example.invalid" TargetMode="External"/></Relationships>',
            'ppt/slides/slide1.xml':'<sld><p><t>İkinci fikir</t></p></sld>','ppt/slides/slide2.xml':'<sld><p><t>Keşif rotası</t></p></sld>'})
        text=office_text(path)
        self.assertLess(text.index('Keşif'),text.index('İkinci'))
    def test_entities_and_oversize_archive_rejected(self):
        path=self.package('danger.docx',{'word/document.xml':'<!DOCTYPE x [<!ENTITY a SYSTEM "file:///private">]><document><p><t>&a;</t></p></document>'})
        with self.assertRaisesRegex(ValueError,'varlık'):office_text(path)
        path=self.package('huge.docx',{'word/document.xml':'x'*(17*1024*1024)})
        with self.assertRaisesRegex(ValueError,'XML'):office_text(path)
    def test_only_successful_workflow_outputs_are_indexed(self):
        good=self.root/'12_ISLER/Ciktilar/good';bad=good.parent/'bad';running=good.parent/'running'
        for folder in (good,bad,running):folder.mkdir(parents=True);(folder/'okunan-metin.txt').write_text('ÖzgünOCRKelimesi',encoding='utf-8')
        (good/'islem-raporu.json').write_text('{"completed":true}')
        (bad/'islem-raporu.json').write_text('{"completed":false}')
        library=Library(self.root);library.index()
        self.assertEqual(['12_ISLER/Ciktilar/good/okunan-metin.txt'],[x['path'] for x in library.search('ÖzgünOCRKelimesi')])
    def test_ocr_limits_missing_engine_and_cancel(self):
        Image.new('RGB',(10,10),'white').save(self.folder/'small.png')
        with self.assertRaises(ValueError):ocr.inspect(self.folder/'small.png',{'language':'tur'},['eng'])
        with self.assertRaises(ValueError):ocr.inspect(self.folder/'small.png',{'rotation':45},['tur','eng'])
        flow=Workflows(self.root,lambda:[],lambda:None)
        with self.assertRaisesRegex(ValueError,'paket'):flow.preview({'kind':'ocr','files':['04_PROJELER/Belgeler/small.png']})
        flow.job={'status':'running','kind':'ocr'};flow.cancel_current();self.assertTrue(flow.cancel.is_set())


@unittest.skipUnless(os.environ.get('ATOLYE_OCR_TEST_ROOT'),'Real Tesseract integration uses an explicitly supplied local kit')
class RealOCRTests(unittest.TestCase):
    def test_turkish_image_and_scanned_pdf_text_and_search(self):
        kit=Path(os.environ['ATOLYE_OCR_TEST_ROOT'])
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'01_TASINABILIR').mkdir()
            # Only the explicit official local OCR engine is referenced by the integration fixture.
            import shutil
            shutil.copytree(kit/'01_TASINABILIR/Tesseract',root/'01_TASINABILIR/Tesseract')
            folder=root/'inputs';folder.mkdir()
            image=Image.new('RGB',(2400,1300),'white');draw=ImageDraw.Draw(image)
            font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',65)
            for i,line in enumerate(['ATOLYE BELGE OKUMA','İstanbul İzmir Ankara','Türkçe: ç ğ ı ö ş ü Ç Ğ İ Ö Ş Ü','Sözleşme tutarı 12500 TL','Referans: NAVIS4837']):
                draw.text((120,120+i*180),line,font=font,fill='black')
            image.save(folder/'Turkce.png');image.save(folder/'Tarama.pdf',resolution=200)
            self.assertFalse(PdfReader(folder/'Tarama.pdf').pages[0].extract_text())
            flow=Workflows(root,lambda:[],lambda:None)
            files=['inputs/Turkce.png','inputs/Tarama.pdf'];before=[fingerprint(root/p) for p in files]
            plan=flow.preview({'kind':'ocr','files':files,'options':{'language':'tur+eng','rotation':0}})
            self.assertEqual(2,plan['pages']);flow.start(plan['id']);flow.worker.join(timeout=90)
            job=flow.current();self.assertEqual('complete',job['status'],job)
            text=(root/job['output']/'okunan-metin.txt').read_text(encoding='utf-8')
            self.assertEqual(2,text.count('NAVIS4837'));self.assertIn('İstanbul',text);self.assertIn('12500',text)
            pdf=PdfReader(root/job['output']/'aranabilir.pdf')
            self.assertEqual(2,len(pdf.pages));self.assertTrue(all('NAVIS4837' in p.extract_text() for p in pdf.pages))
            self.assertEqual(before,[fingerprint(root/p) for p in files])
            library=Library(root);library.index();self.assertTrue(library.search('NAVIS4837'))


if __name__=='__main__':unittest.main()
