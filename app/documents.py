"""Bounded OOXML text extraction. No Office, macros, formula evaluation or links."""
import posixpath
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

OFFICE_EXT={'.docx','.xlsx','.pptx'}
MAX_TEXT=120000


class OfficeArchive:
    def __init__(self,path):
        self.zip=zipfile.ZipFile(path)
        self.read_bytes=0
        infos=self.zip.infolist()
        try:
            if len(infos)>3000 or len({i.filename for i in infos})!=len(infos) or sum(i.file_size for i in infos)>64*1024*1024:
                raise ValueError('Office arşivi güvenli okuma sınırını aşıyor.')
            if any(i.flag_bits&1 for i in infos):raise ValueError('Şifreli Office dosyası okunamaz.')
        except Exception:
            self.zip.close()
            raise
    def xml(self,name):
        info=self.zip.getinfo(name)
        if info.file_size>16*1024*1024:raise ValueError('Office XML boyutu sınırı aşıyor.')
        self.read_bytes+=info.file_size
        if self.read_bytes>64*1024*1024:raise ValueError('Office toplam XML okuma sınırı aşıldı.')
        data=self.zip.read(info)
        # XML entity/declaration variants, including UTF-16, are rejected.
        probe=data.replace(b'\x00',b'').upper()
        if b'<!DOCTYPE' in probe or b'<!ENTITY' in probe:raise ValueError('Office XML varlık tanımları desteklenmez.')
        return ET.fromstring(data)
    def __enter__(self):return self
    def __exit__(self,*args):self.zip.close()


def local(tag):return tag.rsplit('}',1)[-1]
def paragraphs(tree):
    return '\n'.join(''.join(n.text or '' for n in p.iter() if local(n.tag)=='t')
                     for p in tree.iter() if local(p.tag)=='p')


def ordered_parts(archive,base,listing,element):
    rels=archive.xml(base+'/_rels/'+listing+'.rels')
    targets={r.get('Id'):posixpath.normpath(r.get('Target','').lstrip('/') if r.get('Target','').startswith('/') else base+'/'+r.get('Target','')) for r in rels
             if r.get('TargetMode')!='External'}
    tree=archive.xml(base+'/'+listing)
    for node in tree.iter():
        if local(node.tag)==element:
            id=next((v for k,v in node.attrib.items() if k.endswith('}id')),None)
            target=targets.get(id,'')
            if target.startswith(base+'/') and target in archive.zip.namelist():yield node,target


def office_text(path):
    suffix=Path(path).suffix.lower()
    pieces=[]
    length=0
    def append(value):
        nonlocal length
        pieces.append(value)
        length+=len(value)+1
        return length>=MAX_TEXT
    with OfficeArchive(path) as archive:
        if suffix=='.docx':
            append(paragraphs(archive.xml('word/document.xml')))
            for name in sorted(archive.zip.namelist()):
                if re.fullmatch(r'word/(header|footer)\d+\.xml',name):
                    if append(paragraphs(archive.xml(name))):break
        elif suffix=='.pptx':
            for index,(node,name) in enumerate(ordered_parts(archive,'ppt','presentation.xml','sldId')):
                if index>=500:break
                if append(f'[Slayt {index+1}]\n'+paragraphs(archive.xml(name))):break
        elif suffix=='.xlsx':
            shared=[]
            if 'xl/sharedStrings.xml' in archive.zip.namelist():
                shared=[''.join(n.text or '' for n in si.iter() if local(n.tag)=='t')
                        for si in archive.xml('xl/sharedStrings.xml')]
            cells=0
            for sheet_index,(node,name) in enumerate(ordered_parts(archive,'xl','workbook.xml','sheet')):
                if sheet_index>=500:break
                if append('[Sayfa: '+node.get('name','')+']'):break
                for row in archive.xml(name).iter():
                    if local(row.tag)!='row':continue
                    values=[]
                    for cell in row:
                        if local(cell.tag)!='c':continue
                        cells+=1
                        if cells>100000:break
                        value=next((n.text or '' for n in cell if local(n.tag)=='v'),'')
                        if cell.get('t')=='s':
                            try:value=shared[int(value)] if int(value)>=0 else ''
                            except (ValueError,IndexError):value=''
                        elif cell.get('t')=='inlineStr':value=''.join(n.text or '' for n in cell.iter() if local(n.tag)=='t')
                        if value:values.append(value)
                    if append(' | '.join(values)) or cells>100000:break
                if length>=MAX_TEXT or cells>100000:break
        else:raise ValueError('DOCX, XLSX veya PPTX seç.')
    return '\n'.join(pieces)[:MAX_TEXT]
