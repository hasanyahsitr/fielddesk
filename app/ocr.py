"""Offline Tesseract OCR on images/PDF with bounded rendering and cancellation."""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import tempfile
import threading
import time

MAX_PAGES=50
MAX_PIXELS=40_000_000


class Cancelled(Exception):pass


def status(root):
    folder=Path(root)/'01_TASINABILIR/Tesseract'
    try:folder=folder.resolve();inside=folder.is_relative_to(Path(root).resolve())
    except OSError:inside=False
    languages=[l for l in ('tur','eng') if (folder/'tessdata'/(l+'.traineddata')).is_file()]
    try:__import__('pypdfium2');renderer=True
    except (ImportError,OSError):renderer=False
    ready=inside and (folder/'tesseract.exe').is_file() and bool(languages) and renderer
    return {'ready':ready,'module':'Tesseract + PDFium','languages':languages,'renderer':renderer,
            'message':'Hazır' if ready else 'Çantaya Tesseract, dil dosyaları ve pypdfium2 eklenmeli.'}


def inspect(path,options,available):
    language=options.get('language','tur+eng')
    rotation=int(options.get('rotation',0))
    if language not in ('tur','eng','tur+eng') or not set(language.split('+'))<=set(available):
        raise ValueError('Hazır olan Türkçe/İngilizce dilini seç.')
    if rotation not in (0,90,180,270):raise ValueError('Geçerli bir döndürme açısı seç.')
    from PIL import Image,ImageOps
    if Path(path).suffix.lower()=='.pdf':
        from pypdf import PdfReader
        reader=PdfReader(path)
        if reader.is_encrypted:raise ValueError('Şifreli PDF OCR için desteklenmiyor.')
        count=len(reader.pages)
        if not 1<=count<=MAX_PAGES:raise ValueError('OCR için tek işlemde en fazla 50 sayfa seç.')
        for page in reader.pages:
            width,height=float(page.mediabox.width),float(page.mediabox.height)
            if width<=0 or height<=0 or width*height*(300/72)**2>MAX_PIXELS:
                raise ValueError('PDF sayfası 300 DPI / 40 megapiksel sınırını aşıyor.')
    else:
        with Image.open(path) as image:
            if getattr(image,'n_frames',1)!=1:raise ValueError('Hareketli/çok kareli görsel OCR için desteklenmiyor.')
            if image.width*image.height>MAX_PIXELS:raise ValueError('OCR görseli en fazla 40 megapiksel olabilir.')
        count=1
    return count,{'language':language,'rotation':rotation,'dpi':300}


def recognize(root,files,output,options,progress,cancel):
    from PIL import Image,ImageOps
    from pypdf import PdfReader,PdfWriter
    import pypdfium2 as pdfium
    binary=Path(root)/'01_TASINABILIR/Tesseract/tesseract.exe'
    folder=binary.parent
    if not status(root)['ready']:raise ValueError('OCR motoru artık bulunamıyor.')
    env=os.environ.copy();env['TESSDATA_PREFIX']=str(folder/'tessdata');env['OMP_THREAD_LIMIT']='2'
    texts=[];page_pdfs=[];done=0;warnings=[]
    with tempfile.TemporaryDirectory(prefix='.ocr-',dir=output) as temp:
        temp=Path(temp)
        for file in files:
            path=Path(root)/file['path']
            document=None
            try:
                if path.suffix.lower()=='.pdf':document=pdfium.PdfDocument(path.read_bytes())
                for index in range(file['pages']):
                    if cancel.is_set():raise Cancelled('İşlem iptal edildi. Kaynak dosyalar korundu.')
                    page=bitmap=None
                    try:
                        if document is not None:
                            page=document[index]
                            w,h=page.get_size()
                            if w*h*(300/72)**2>MAX_PIXELS:raise ValueError('PDF sayfası render sınırını aşıyor.')
                            bitmap=page.render(scale=300/72)
                            image=bitmap.to_pil().copy()
                        else:
                            with Image.open(path) as original:image=ImageOps.exif_transpose(original).convert('RGBA')
                        rgba=image.convert('RGBA');image.close()
                        image=Image.new('RGB',rgba.size,'white');image.paste(rgba,mask=rgba.getchannel('A'));rgba.close()
                        if options['rotation']:
                            rotated=image.rotate(-options['rotation'],expand=True,fillcolor='white');image.close();image=rotated
                        stem=temp/f'page-{done+1:04d}'
                        image.save(stem.with_suffix('.png'),dpi=(300,300));image.close()
                    finally:
                        if bitmap:bitmap.close()
                        if page:page.close()
                    progress(done,f'{file["name"]} · {index+1}/{file["pages"]} sayfa okunuyor…')
                    command=[str(binary),str(stem.with_suffix('.png')),str(stem),'--tessdata-dir',str(folder/'tessdata'),
                             '-l',options['language'],'--oem','1','--psm','3','--dpi','300','txt','pdf']
                    log=stem.with_suffix('.log')
                    with log.open('wb') as stderr:
                        child=subprocess.Popen(command,cwd=folder,env=env,stdout=subprocess.DEVNULL,stderr=stderr,
                                               creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                        started=time.monotonic()
                        try:
                            while child.poll() is None:
                                if cancel.wait(.15):raise Cancelled('İşlem iptal edildi. Kaynak dosyalar korundu.')
                                if time.monotonic()-started>120:raise TimeoutError('OCR sayfası 120 saniyede tamamlanamadı.')
                        finally:
                            if child.poll() is None:child.terminate();child.wait(timeout=10)
                    if child.returncode:raise ValueError('OCR motoru hata verdi: '+log.read_text(encoding='utf-8',errors='replace')[-500:])
                    text=stem.with_suffix('.txt').read_text(encoding='utf-8').strip()
                    if not text:warnings.append(f'{file["name"]} / {index+1}: metin bulunamadı.')
                    texts.append(f'[{file["name"]} — Sayfa {index+1}]\n{text}')
                    page_pdfs.append(stem.with_suffix('.pdf'));done+=1
                    progress(done,f'{done} sayfa tamamlandı.')
            finally:
                if document is not None:document.close()
        if cancel.is_set():raise Cancelled('İşlem iptal edildi. Kaynak dosyalar korundu.')
        text_path=output/'okunan-metin.txt'
        text_path.write_text('\n\n'.join(texts)+'\n',encoding='utf-8')
        writer=PdfWriter()
        for path in page_pdfs:
            if cancel.is_set():writer.close();raise Cancelled('İşlem iptal edildi. Kaynak dosyalar korundu.')
            writer.append(str(path))
        target=output/'aranabilir.pdf'
        with target.open('xb') as stream:writer.write(stream)
        writer.close()
        if cancel.is_set():raise Cancelled('İşlem iptal edildi. Kaynak dosyalar korundu.')
        with target.open('rb') as stream:
            if len(PdfReader(stream).pages)!=done:raise ValueError('OCR çıktı sayfa sayısı uyuşmuyor.')
    return [text_path,target],warnings,'\n\n'.join(texts)[:5000],done
