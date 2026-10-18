#!/usr/bin/env python3
"""Produce cropped previews and a contact sheet for editorial photo review.
Keep all originals untouched; never retouch a face. The page uses preview webp.
"""
import json, re, math
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets/photos'
OUT=ROOT/'assets/gallery'
OUT.mkdir(parents=True,exist_ok=True)
candidates=[p for p in sorted(SRC.iterdir(),key=lambda p:p.name.lower()) if p.suffix.lower() in {'.png','.jpg','.jpeg','.webp'}]
records=[]; tiles=[]
for p in candidates:
 try:
  with Image.open(p) as raw:
   im=ImageOps.exif_transpose(raw).convert('RGB')
   orig=im.size
   im.thumbnail((1400,1050),Image.Resampling.LANCZOS)
   target=OUT/(re.sub('[^A-Za-z0-9_-]','-',p.stem)+'.webp')
   im.save(target,'WEBP',quality=82,method=6)
   thumb=ImageOps.contain(im,(364,220),Image.Resampling.LANCZOS)
   tile=Image.new('RGB',(390,274),'#e5e5df')
   tile.paste(thumb,((390-thumb.width)//2,8+(220-thumb.height)//2))
   draw=ImageDraw.Draw(tile)
   draw.text((12,235),p.name[:46],fill='#222720')
   draw.text((12,251),f'{orig[0]} x {orig[1]}',fill='#515951')
   tiles.append(tile)
   records.append({'id':p.stem,'original':'assets/photos/'+p.name,'image':'assets/gallery/'+target.name,
                   'width':im.width,'height':im.height,'caption':p.stem.replace('_',' ')})
   print(p.name,'=>',target.name,orig,'to',im.size)
 except Exception as err: print('SKIP',p.name,str(err))
columns=4; rows=math.ceil(len(tiles)/columns)
sheet=Image.new('RGB',(columns*390,rows*274),'#f4f4ef')
for i,tile in enumerate(tiles):sheet.paste(tile,((i%columns)*390,(i//columns)*274))
sheet.save(OUT/'review-contact.jpg','JPEG',quality=76,optimize=True)
(ROOT/'data/gallery.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n','utf8')
print('Number of photos:',len(records),'contact sheet bytes:',(OUT/'review-contact.jpg').stat().st_size)
