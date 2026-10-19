#!/usr/bin/env python3
"""Render PNG favicons from the branded DKK monogram using Pillow.
SVG remains the source of truth for modern browsers.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
FONTS=[
    '/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
]

def font(size):
    for p in FONTS:
        if Path(p).is_file():
            return ImageFont.truetype(p,size=size)
    return ImageFont.load_default()

def make_icon(side,file,rounding):
    scale=4
    s=side*scale
    canvas=Image.new('RGB',(s,s),(32,43,37))
    draw=ImageDraw.Draw(canvas)
    # Fill outside rounded corners with the same dark background; icon
    # remains legible on dark/light browser tabs and mobile launch screens.
    glyph=font(round(s*.37))
    rect=draw.textbbox((0,0),'DKK',font=glyph,stroke_width=0)
    tw=rect[2]-rect[0]
    th=rect[3]-rect[1]
    draw.text(((s-tw)/2-rect[0], s*.46-th/2-rect[1]),
              'DKK', font=glyph, fill=(241,234,220),stroke_width=0)
    draw.line((s*.17,s*.78,s*.83,s*.78),fill=(197,170,133),width=max(3,s//70))
    canvas=canvas.resize((side,side),Image.Resampling.LANCZOS)
    canvas.save(ASSETS/file,format='PNG',optimize=True)
    print(file,canvas.size)

make_icon(32,'favicon-32x32.png',4)
make_icon(48,'favicon-48x48.png',6)
make_icon(180,'apple-touch-icon.png',12)
