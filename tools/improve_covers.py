#!/usr/bin/env python3
"""Find genuine higher-quality covers for DKK's already-published books.

Never generates or substitutes invented artwork. Candidates come from the exact
Google Play Books volume ID and Apple Books product ID recorded in the catalogue.
New images are used only if title/author can be checked and quality improves.
Original cover files remain untouched. No login or commercial API key needed.

Runs on GitHub Actions (internet-enabled), not on a visitor's device.
"""
from __future__ import annotations
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
from PIL import Image, ImageOps, ImageStat
from io import BytesIO
from difflib import SequenceMatcher
import json, re, time, unicodedata, math

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/publications.json'
OUT=ROOT/'assets/verified-covers'
OUT.mkdir(parents=True,exist_ok=True)
USER_AGENT='Mozilla/5.0 (compatible; DKK cover verifier; https://dkk.hqici.com)'
TIMEOUT=12

def request(url,limit=4_000_000):
    req=Request(url,headers={'User-Agent':USER_AGENT,
      'Accept':'application/json,image/jpeg,image/png,image/webp,*/*'})
    with urlopen(req,timeout=TIMEOUT) as resp:
        data=resp.read(limit+1)
        if len(data)>limit:raise ValueError('Response too large')
        return data

def normalized(s):
    t=unicodedata.normalize('NFKD',str(s or '').lower())
    return re.sub(r'[^a-z0-9 ]+',' ',''.join(c for c in t if not unicodedata.combining(c))).strip()

def same_title(candidate,expected):
    a=normalized(candidate)
    b=normalized(expected)
    return bool(a and b) and (a in b or b in a or SequenceMatcher(None,a,b).ratio()>=.65)

def same_author(authors):
    return any('kolodziej' in normalized(v).replace(' ','') for v in authors)

def get_book_ids(p,platform):
    result=[]
    for l in p.get('links',[]):
        if l.get('label')!=platform:continue
        parsed=urlparse(l.get('url',''))
        if platform=='Google Play Books' and parsed.hostname=='play.google.com':
            id=parse_qs(parsed.query).get('id',[''])[0]
            if re.fullmatch(r'[A-Za-z0-9_-]{8,20}',id):result.append(id)
        if platform=='Apple Books' and parsed.hostname=='books.apple.com':
            m=re.search(r'/id(\d{8,14})',parsed.path)
            if m:result.append(m.group(1))
    return list(dict.fromkeys(result))

def score(image):
    img=ImageOps.exif_transpose(image).convert('RGB')
    w,h=img.size
    if w<160 or h<180 or w/h>1.6 or h/w>2.25:
        return -1
    thumb=img.copy();thumb.thumbnail((140,140))
    pixels=list(thumb.getdata())
    pale=sum(1 for r,g,b in pixels if min(r,g,b)>241)/max(1,len(pixels))
    # This detects monochrome placeholder images but does NOT mean a
    # legitimate minimalist published cover is invalid.
    st=ImageStat.Stat(thumb)
    diversity=sum(st.stddev)/3
    resolution=min(w*h,1000*1400)
    return math.log2(resolution)*11 + diversity*.13 - pale*12

def get_img(url):
    data=request(url)
    with Image.open(BytesIO(data)) as im:
        im.load()
        return ImageOps.exif_transpose(im).convert('RGB')

def candidates(p):
    title=p['title']['en']
    for aid in get_book_ids(p,'Apple Books'):
        try:
            obj=json.loads(request('https://itunes.apple.com/lookup?id='+aid+'&entity=ebook').decode())
            for entry in obj.get('results',[]):
                if str(entry.get('trackId',''))!=aid:continue
                a=entry.get('artistName','')
                if not same_title(entry.get('trackName',''),title) or not same_author([a]):continue
                artwork=entry.get('artworkUrl100') or entry.get('artworkUrl60')
                if artwork:
                    yield ('Apple Books',artwork.replace('100x100bb','1200x1200bb').replace('60x60bb','1200x1200bb'))
                    yield ('Apple Books',artwork.replace('100x100bb','600x600bb').replace('60x60bb','600x600bb'))
        except Exception as exc:
            print(p['slug'],'Apple verification unavailable:',str(exc)[:100])
    for gid in get_book_ids(p,'Google Play Books'):
        try:
            obj=json.loads(request('https://www.googleapis.com/books/v1/volumes/'+gid).decode())
            info=obj.get('volumeInfo',{})
            if not same_author(info.get('authors',[])) or not same_title(info.get('title',''),title):
                print(p['slug'],'Google metadata not confidently matched; skipping')
                continue
            urls=info.get('imageLinks',{})
            for size in ('extraLarge','large','medium','small','thumbnail','smallThumbnail'):
                url=urls.get(size)
                if url:
                    yield ('Google Books',url.replace('http://','https://',1))
            for zoom in (3,2,1):
                yield ('Google Books','https://books.google.com/books/content?id='+gid+'&printsec=frontcover&img=1&zoom='+str(zoom)+'&source=gbs_api')
        except Exception as exc:
            print(p['slug'],'Google verification unavailable:',str(exc)[:100])

def main():
    works=json.loads(DATA.read_text('utf-8'))
    changed=0
    for p in works:
        if p.get('status')!='published':continue
        current=ROOT/p['cover']
        if not current.is_file():
            print('MISSING cover',p['slug'])
            continue
        try:
            with Image.open(current) as img:
                old_score=score(img)
                size=img.size
        except Exception:
            old_score=-1;size=(0,0)
        strongest=(old_score,None,None)
        print('\n',p['slug'],'current=',size,'score=',round(old_score,1))
        seen=set()
        for origin,url in candidates(p):
            if url in seen:continue
            seen.add(url)
            try:
                pic=get_img(url)
                merit=score(pic)
                print(' candidate',origin,pic.size,'score',round(merit,1))
                # The present cover is already a legitimate source. Don't
                # replace it with equal/lower-resolution art or near clones.
                if merit>strongest[0]+5 and pic.width>=300 and pic.height>=350:
                    strongest=(merit,origin,pic)
            except Exception as exc:
                print(' candidate rejected',origin,type(exc).__name__)
            time.sleep(.08)
        _,origin,img=strongest
        if img is None:
            print(' No verified higher-quality art. Kept',p['cover'])
            continue
        img.thumbnail((900,1350),Image.Resampling.LANCZOS)
        dst=OUT/(p['slug']+'.jpg')
        img.save(dst,'JPEG',quality=90,optimize=True,progressive=True)
        p['cover']='assets/verified-covers/'+p['slug']+'.jpg'
        p['coverSource']=origin
        changed+=1
        print(' NEW VERIFIED COVER',dst.relative_to(ROOT),img.size,'via',origin)
    if changed:
        DATA.write_text(json.dumps(works,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Improved',changed,'published covers; unchanged covers remain original')
if __name__=='__main__':main()
