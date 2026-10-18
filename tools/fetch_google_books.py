#!/usr/bin/env python3
"""Import public Google Books metadata and cover art for supplied Google Play IDs.
Title/author assignments are accepted only when the catalogue author matches Kolodziej.
Failures are explicit. No commercial API keys, runtime servers, or framework required.
"""
import io,json,re,time,unicodedata
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
SITE=json.loads((ROOT/'data/site.json').read_text('utf8'))
IDS=SITE.get('googlePlayBooks',[])
OUT=ROOT/'assets/google-books'
OUT.mkdir(parents=True,exist_ok=True)
USER_AGENT='DKKPersonalArchive/1.0 (metadata import; contact in ORCID record)'
def request(url,timeout=16):
 req=Request(url,headers={'User-Agent':USER_AGENT,'Accept':'application/json,image/jpeg,image/png,image/webp,*/*'})
 with urlopen(req,timeout=timeout) as resp:
  return resp.read(),resp.headers.get('Content-Type','')
def same_author(s):
 t=unicodedata.normalize('NFKD',s.lower())
 return 'kolodziej' in ''.join(ch for ch in t if not unicodedata.combining(ch))
records=[]
for idx,id in enumerate(IDS):
 if not re.fullmatch(r'[A-Za-z0-9_-]{8,20}',id):
  print('Skipped invalid ID:',repr(id));continue
 entry={'id':id,'url':'https://play.google.com/store/books/details?id='+id,'title':None,'authors':[],'cover':None}
 try:
  raw,_=request('https://www.googleapis.com/books/v1/volumes/'+id)
  book=json.loads(raw)
  info=book.get('volumeInfo') or {}
  authors=info.get('authors') or []
  entry['authors']=authors
  if any(same_author(a) for a in authors):
   entry['title']=info.get('title')
  else:
   print('Title not attributed without author match:',id,authors)
  imageLinks=info.get('imageLinks') or {}
  urls=[imageLinks.get(x) for x in ('large','medium','small','thumbnail','smallThumbnail')]
 except Exception as error:
  print('Google Books metadata unavailable:',id,repr(error))
  urls=[]
 urls=[u.replace('http://','https://',1) for u in urls if isinstance(u,str)]
 urls.append('https://books.google.com/books/content?id='+id+'&printsec=frontcover&img=1&zoom=2&source=gbs_api')
 for coverUrl in urls:
  try:
   raw,typ=request(coverUrl)
   if len(raw)<2500: raise ValueError('Image response too small')
   with Image.open(io.BytesIO(raw)) as image:
    image.load()
    if image.width<90 or image.height<125: raise ValueError('Thumbnail too small')
    image=ImageOps.exif_transpose(image).convert('RGB')
    image.thumbnail((650,920),Image.Resampling.LANCZOS)
    dst=OUT/(id+'.jpg')
    image.save(dst,'JPEG',quality=87,optimize=True)
    entry['cover']='assets/google-books/'+id+'.jpg'
   break
  except Exception as error:
   print('Cover URL not usable:',id,type(error).__name__)
 records.append(entry)
 print(id,'title=',entry['title'],'cover=',entry['cover'])
 (ROOT/'data/google-books.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Imported',len(records),'Google Play entries')
