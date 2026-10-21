"""Generate one genuine-portrait social preview for every bilingual DKK webpage.
Run last in the site build so subsequent regeneration preserves the universal OG image.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import re

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 630
OUTPUT = ROOT / 'assets/social/dawid-kolodziej-og.jpg'
URL = 'https://dkk.hqici.com/assets/social/dawid-kolodziej-og.jpg'

def font(size, serif=False, italic=False):
    if serif and italic:
        names = ['/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',
                 '/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf']
    elif serif:
        names = ['/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
                 '/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf']
    else:
        names = ['/usr/share/fonts/truetype/lato/Lato-Regular.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()

def make_image():
    source = ROOT / 'assets/DawidKolodziej.png'
    if not source.is_file():
        raise FileNotFoundError(f'Author photo not found: {source}')
    im = Image.new('RGB', (W, H), (20, 34, 31))
    d = ImageDraw.Draw(im)
    for x in range(W):
        k = x / W
        d.line((x, 0, x, H), fill=(int(25-9*k), int(40-14*k), int(36-11*k)))
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((-280, -240, 900, 950), fill=(160, 136, 91, 21))
    od.ellipse((620, -100, 1360, 790), fill=(194, 159, 107, 13))
    im = Image.alpha_composite(im.convert('RGBA'), overlay.filter(ImageFilter.GaussianBlur(100)))
    d = ImageDraw.Draw(im)
    cream, gold, muted = (250, 248, 240), (229, 192, 146), (194, 204, 196)
    d.line((57, 101, 713, 101), fill=(95, 110, 99), width=1)
    d.line((55, 159, 103, 159), fill=(190, 164, 119), width=2)
    d.text((55, 30), 'DKK.', font=font(49, serif=True), fill=cream)
    d.text((210, 61), 'PROFESSIONAL  /  PROFILE', font=font(12), fill=muted)
    d.text((55, 132), 'MENTAL HEALTH  ·  EDUCATION  ·  LEADERSHIP', font=font(13), fill=gold)
    original = Image.open(source).convert('RGB')
    pw, ph = 411, 489
    photo = ImageOps.fit(original, (pw, ph), Image.Resampling.LANCZOS, centering=(0.5, 0.38))
    photo = ImageEnhance.Contrast(ImageEnhance.Color(photo).enhance(0.92)).enhance(1.04)
    mask = Image.new('L', (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw-1, ph-1), radius=3, fill=255)
    x, y = 745, 67
    d.rectangle((x+12, y+14, x+pw+12, y+ph+14), outline=(120, 122, 96), width=1)
    im.paste(photo, (x, y), mask)
    d.line((x, y+ph+1, x+pw, y+ph+1), fill=(190, 164, 119), width=2)
    d.text((54, 203), 'Dawid Karol', font=font(79, serif=True), fill=cream)
    d.text((54, 288), 'Kołodziej.', font=font(99, serif=True, italic=True), fill=gold)
    d.line((58, 433, 660, 433), fill=(138, 132, 105), width=1)
    d.text((57, 458), 'PSYCHOTHERAPIST  ·  MENTAL HEALTH CLINICIAN', font=font(15), fill=cream)
    d.text((57, 488), 'AUTHOR  ·  ORGANISATIONAL LEADER', font=font(15), fill=muted)
    d.text((57, 574), 'dkk.hqici.com', font=font(23, serif=True), fill=cream)
    d.text((558, 586), 'AUSTRALIA', font=font(11), fill=gold)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    im.convert('RGB').save(OUTPUT, 'JPEG', quality=88, optimize=True, progressive=True, subsampling=0)
    assert 30_000 < OUTPUT.stat().st_size < 900_000
    print(f'Generated {OUTPUT.relative_to(ROOT)}, {OUTPUT.stat().st_size} bytes')

def update_html():
    metadata = (
        '<meta property="og:image:secure_url" content="'+URL+'">'
        '<meta property="og:image:type" content="image/jpeg">'
        '<meta property="og:image:width" content="1200">'
        '<meta property="og:image:height" content="630">'
        '<meta property="og:image:alt" content="Dawid Karol Kołodziej — psychotherapist, mental health clinician, author and organisational leader">'
        '<meta name="twitter:image" content="'+URL+'">'
        '<meta name="twitter:image:alt" content="Dawid Karol Kołodziej — professional profile">'
        '<meta property="og:site_name" content="Dawid Karol Kołodziej">'
    )
    count = 0
    for page in sorted(ROOT.rglob('index.html')):
        if any(part.startswith('.') for part in page.relative_to(ROOT).parts):
            continue
        original = page.read_text('utf-8')
        if '<head' not in original or '</head>' not in original:
            continue
        html = original
        for prop in ('og:image:secure_url', 'og:image:type', 'og:image:width',
                     'og:image:height', 'og:image:alt', 'og:site_name'):
            html = re.sub(r'<meta\s+property="'+re.escape(prop)+r'"\s+content="[^"]*">', '', html)
        for name in ('twitter:image', 'twitter:image:alt'):
            html = re.sub(r'<meta\s+name="'+re.escape(name)+r'"\s+content="[^"]*">', '', html)
        if re.search(r'<meta\s+property="og:image"\s+content="[^"]*">', html):
            html = re.sub(r'<meta\s+property="og:image"\s+content="[^"]*">',
                          '<meta property="og:image" content="'+URL+'">', html)
        else:
            html = html.replace('</head>', '<meta property="og:image" content="'+URL+'"></head>', 1)
        html = html.replace('</head>', (metadata if page.relative_to(ROOT).as_posix().startswith('pl/') else metadata.replace('Kołodziej', 'Kolodziej'))+'</head>', 1)
        if html != original:
            page.write_text(html, 'utf-8')
            count += 1
        assert html.count('<meta property="og:image" content="'+URL+'">') == 1, page
        assert html.count('name="twitter:image"') == 1, page
    assert count >= 20, f'Expected all bilingual main and publication pages, got {count}'
    print(f'Universal personal OG image applied to {count} pages')

if __name__ == '__main__':
    make_image()
    update_html()
