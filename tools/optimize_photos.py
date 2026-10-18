#!/usr/bin/env python3
"""Generate reusable WebP crops of the actual photographs, keeping the originals.
Requires Pillow only when producing image assets; the website remains static.
"""
from pathlib import Path
from PIL import Image, ImageOps
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets"/"portraits"
OUT.mkdir(parents=True,exist_ok=True)
# (source, output name, desired dimensions, focal centre)
photos=[
 ("assets/DawidKolodziej.png","hero.webp",(1050,1312),(.5,.32)),
 ("assets/photos/1779784543811.png","about.webp",(850,1100),(.56,.47)),
 ("assets/photos/42.png","speaking.webp",(960,640),(.50,.45)),
 ("assets/photos/IMG_1534.jpg","candid.webp",(800,1000),(.52,.40)),
]
for rel,target,dimensions,focal in photos:
 src=ROOT/rel
 if not src.is_file():
  print("Missing, skipped:",src)
  continue
 with Image.open(src) as original:
  im=ImageOps.exif_transpose(original)
  # Never retouch a person's features; geometric crop + scaling only.
  if im.mode not in ("RGB","RGBA"):
   im=im.convert("RGB")
  elif im.mode=="RGBA":
   base=Image.new("RGBA",im.size,"#25332d")
   im=Image.alpha_composite(base,im).convert("RGB")
  cropped=ImageOps.fit(im,dimensions,method=Image.Resampling.LANCZOS,centering=focal)
  path=OUT/target
  cropped.save(path,format="WEBP",quality=84,method=6)
  print(rel,"->",path.relative_to(ROOT),path.stat().st_size,"bytes")
