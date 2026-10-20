#!/usr/bin/env python3
"""Normalise author-provided covers, match numbered PNGs to verified catalogue titles.
Run in GitHub Actions with Pillow and Tesseract. Never guess an unmatched book cover.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageOps
import difflib
import itertools
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
CATALOGUE=ROOT/'data/publications.json'
COVERS=ROOT/'assets/book_covers'
AUTHORED=ROOT/'assets/author-covers'
STOP={'from','with','the','and','into','between','without','toward','towards','for','the','your','this','that','each','based','their','what','how','are'}
def words(s):
    return [x for x in re.findall(r'[a-z0-9]+',str(s).lower()) if len(x)>=4 and x not in STOP]
def generate_webp(source,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    with Image.open(source) as opened:
        image=ImageOps.exif_transpose(opened)
        if image.mode not in ('RGB','RGBA'):
            image=image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
        image.thumbnail((1600,2000),Image.Resampling.LANCZOS)
        image.save(dest,format='WEBP',quality=85,method=6)
    print('  WEBP',dest.relative_to(ROOT),dest.stat().st_size)
def ocr(image):
    bits=[]
    for psm in ('3','6','11'):
        r=subprocess.run(['tesseract',str(image),'stdout','--psm',psm],
                         capture_output=True,text=True,check=False)
        if r.returncode==0: bits.append(r.stdout)
    return ' '.join(bits).lower()
def score(recognised,pub):
    ocrwords=words(recognised)
    if not ocrwords:return 0
    title=words(pub['title']['en'])+words(pub.get('titleShort',{}).get('en',''))
    title=list(dict.fromkeys(title))
    n=0
    for token in title:
        matches=[w for w in ocrwords if w==token or (len(w)>=5 and difflib.SequenceMatcher(None,w,token).ratio()>=0.78)]
        if matches: n+=1
    # Stronger weight on distinctive long title tokens; normalized to account for title length
    return round(n/max(2,len(title)) + n*0.065,3) if n>=2 else 0
def main():
    works=json.loads(CATALOGUE.read_text('utf-8'))
    source_pngs=sorted(COVERS.glob('*.png'),key=lambda p:p.name)
    published=[p for p in works if p.get('status')=='published']
    assigned={}
    if source_pngs:
        readings=[ocr(p) for p in source_pngs]
        print('NUMBERED COVER OCR RESULTS')
        for path,t in zip(source_pngs,readings):
            print(' ',path.name,repr(t[:300]))
        candidates=[]
        for img,read in zip(source_pngs,readings):
            for w in published:
                rating=score(read,w)
                if rating>=.35:
                    candidates.append((rating,img,w['slug']))
        candidates.sort(key=lambda x:(-x[0],x[1].name,x[2]))
        taken_images=set();taken_works=set()
        for rating,img,slug in candidates:
            if img.name in taken_images or slug in taken_works:continue
            taken_images.add(img.name);taken_works.add(slug)
            assigned[img.name]=slug
            print('  MATCH',img.name,'=>',slug,'confidence',rating)
    by_slug={p['slug']:p for p in works}
    for png in source_pngs:
        slug=assigned.get(png.name)
        target=COVERS/((slug if slug else png.stem)+'.webp')
        generate_webp(png,target)
        png.unlink()
        if slug:
            entry=by_slug[slug]
            entry['cover']='assets/book_covers/'+target.name
            entry['coverSource']='author-provided'
            entry.pop('coverNote',None)
        else:
            print('  UNMATCHED — kept converted asset; no publication association guessed:',target.name)
    # Any legacy JPG which is still the active selected cover is converted
    # and kept under the same semantic basename.
    for entry in works:
        path=entry.get('cover','')
        if path.startswith('assets/author-covers/') and path.lower().endswith('.jpg'):
            src=ROOT/path
            if src.exists():
                dst=src.with_suffix('.webp')
                if not dst.exists():generate_webp(src,dst)
                entry['cover']=dst.relative_to(ROOT).as_posix()
    # Remove JPGs in author-covers only when they are no longer referenced
    # in publication records; Google Books originals can be retained when
    # referenced by retailer metadata / ingestion workflows.
    referenced={p.get('cover') for p in works}|{p.get('retailerCover') for p in works}
    for jpg in sorted(AUTHORED.glob('*.jpg')):
        if jpg.relative_to(ROOT).as_posix() not in referenced:
            print('  REMOVE unused former cover',jpg.relative_to(ROOT))
            jpg.unlink()
    CATALOGUE.write_text(json.dumps(works,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('COVER MIGRATION COMPLETE; matched',len(assigned),'of',len(source_pngs),'author-provided PNG covers')
if __name__=='__main__':
    main()
