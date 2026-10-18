#!/usr/bin/env python3
"""Generate three editorial pages in EN/PL from checked-in JSON. Python stdlib."""
from pathlib import Path
from html import escape as e
import json
R=Path(__file__).resolve().parents[1]
media=json.loads((R/'data/media.json').read_text('utf-8'))
gallery=json.loads((R/'data/gallery.json').read_text('utf-8'))
roles=json.loads((R/'data/leadership.json').read_text('utf-8'))
routes={'en':{'home':'index.html','leadership':'leadership/','media':'media/','gallery':'gallery/','books':'publications/'},'pl':{'home':'pl/index.html','leadership':'pl/organizacje/','media':'pl/media/','gallery':'pl/galeria/','books':'pl/publikacje/'}}
w={'en':dict(about='About',leadership='Leadership',books='Publications',media='Media',gallery='Gallery',all='All',year='Year',
  media_caption='Original reporting and publicly documented appearances. Broadcaster participation does not imply institutional endorsement.',
  gallery_caption='Archival photographs are distinguished from stylised editorial compositions.',
  back='Back to top'),
   'pl':dict(about='O mnie',leadership='Organizacje',books='Publikacje',media='Media',gallery='Galeria',all='Wszystkie',year='Rok',
  media_caption='Oryginalne materiały i publicznie udokumentowane wystąpienia. Obecność w programie nie oznacza rekomendacji stacji.',
  gallery_caption='Archiwalne fotografie odróżniono od stylizowanych kompozycji redakcyjnych.',
  back='Do góry')}
def prefix(lang):return '../' if lang=='en' else '../../'
def inner_nav(lang,pre):
  return ''.join(f'<a href="{pre+routes[lang][k]+("#about" if k=="home" else "")}">{e(w[lang][label])}</a>' for k,label in [('home','about'),('leadership','leadership'),('books','books'),('media','media'),('gallery','gallery')])
def base(lang,which,title,description,content):
 pre=prefix(lang);target=pre+routes['pl' if lang=='en' else 'en'][which]
 nav=inner_nav(lang,pre)
 page=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="index,follow"><meta name="color-scheme" content="light">
<meta name="description" content="{e(description,quote=True)}">
<title>{e(title)} — Dawid Karol Kołodziej</title><meta property="og:title" content="{e(title,quote=True)} — Dawid Karol Kołodziej">
<meta property="og:description" content="{e(description,quote=True)}"><meta property="og:type" content="website">
<meta property="og:image" content="https://dafudo.github.io/DKKICI/assets/DawidKolodziej.png">
<link rel="icon" type="image/svg+xml" href="{pre}assets/favicon.svg">
<link rel="stylesheet" href="{pre}css/style.css"><link rel="stylesheet" href="{pre}css/identity.css">
<link rel="stylesheet" href="{pre}css/showcase.css"><script>document.documentElement.classList.add('js')</script>
<script defer src="{pre}js/main.js"></script><script defer src="{pre}js/showcase.js"></script></head>
<body id="top" class="showcase-page"><a href="#main" class="skip">Skip to content</a><header class="site-nav"><div class="nav-inner container">
<a class="brand" href="{pre+routes[lang]['home']}" aria-label="Dawid Karol Kołodziej"><span class="brand-mark">DKK.</span><span class="brand-caption">PERSONAL / ARCHIVE</span></a>
<nav class="nav-links" aria-label="Main navigation">{nav}</nav><div class="nav-right">
<a class="locale-link" href="{target}">{'PL' if lang=='en' else 'EN'} ↗</a>
<button class="nav-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="mobile-nav" aria-label="Menu"><span></span><span></span></button></div></div></header>
<div class="mobile-panel" id="mobile-nav" aria-hidden="true"><div class="container"><p class="eyebrow">MENU</p><nav aria-label="Mobile navigation">{nav}</nav></div></div>
<main id="main">{content}</main><footer class="footer"><div class="container"><div class="footer-top">
<a class="footer-brand" href="{pre+routes[lang]['home']}">DKK.</a><nav class="footer-nav" aria-label="Footer navigation">{nav}</nav>
</div><div class="footer-bottom"><span>© Dawid Karol Kołodziej · PERSONAL ARCHIVE</span><a href="#top">↑ {w[lang]['back']}</a></div></div></footer></body></html>'''
 path=R/routes[lang][which]/'index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(page,'utf-8')
def hero(lang,kicker,title,lede,index):
 return f'''<section class="showcase-hero"><div class="container"><p class="showcase-hero__kicker">{e(kicker)}</p>
<h1>{title}</h1><p class="showcase-hero__lede">{e(lede)}</p>
<div class="showcase-hero__bottom"><a href="#collection">{'Explore the collection' if lang=='en' else 'Przeglądaj kolekcję'} ↘</a><span class="showcase-hero__count">{index}</span></div></div></section>'''
def section_head(lang,kicker,title,description):
 return f'''<div class="showcase-section__header"><div><p class="showcase-eyebrow">{e(kicker)}</p><h2>{title}</h2></div><p>{e(description)}</p></div>'''
def leadership(lang):
 pl=lang=='pl';p=prefix(lang)
 top=hero(lang,'DKK / ORGANISATIONS & STRATEGY' if not pl else 'DKK / ORGANIZACJE I STRATEGIA',
   'The work of<br><em>building.</em>' if not pl else 'Praca nad<br><em>rozwojem.</em>',
   'Leading institutions, professional education and organisational projects alongside mental health practice.' if not pl else 'Kierowanie instytucjami, edukacją zawodową i projektami organizacyjnymi obok pracy w obszarze zdrowia psychicznego.','01 / 03')
 cards=''
 for i,r in enumerate(roles,1):
  cards+=f'''<article class="showcase-leader"><span class="showcase-leader__index">{i:02}</span>
<div><p class="showcase-eyebrow">{e(r['title'][lang])} · {r['from']}—</p><h3>{e(r['name'])}</h3></div>
<div class="showcase-leader__copy"><p>{e(r['description'][lang])}</p>
<a class="showcase-outlink" href="{e(r['url'],quote=True)}" target="_blank" rel="noopener noreferrer">{'Organisation / professional profile' if not pl else 'Organizacja / profil zawodowy'} <span>↗</span></a></div></article>'''
 top+='<section id="collection" class="showcase-section"><div class="container">'+section_head(lang,'01 / CORE RESPONSIBILITIES',
   'Institutions with<br><em>purpose.</em>' if not pl else 'Instytucje<br><em>z misją.</em>',
   'Three distinct responsibilities in governance, strategy and academic direction.' if not pl else 'Trzy odrębne odpowiedzialności w zarządzaniu, strategii i rozwoju akademickim.')+'<div class="showcase-leadership">'+cards+'</div></div></section>'
 milestones=[('2009','Charity placements','Praktyki w organizacjach charytatywnych'),('2013','Counselling practice','Praktyka poradnicza'),('2015','TPP presidency','Prezes TPP'),('2024–','Leadership & Australia','Przywództwo i Australia')]
 chips=''.join(f'<div class="showcase-year"><strong>{y}</strong><p>{e(plb if pl else en)}</p></div>' for y,en,plb in milestones)
 top+='<section class="showcase-section showcase-section--deep"><div class="container">'+section_head(lang,'02 / THE PROFESSIONAL JOURNEY',
   'From practice<br><em>to projects.</em>' if not pl else 'Od praktyki<br><em>do projektów.</em>',
   '2009 refers to early charity placements; professional counselling work developed from 2013.' if not pl else 'Rok 2009 oznacza pierwsze praktyki charytatywne; praca zawodowa w poradnictwie rozwijała się od 2013 roku.')
 top+='<div class="showcase-years">'+chips+'</div><div class="showcase-showcase" style="margin-top:65px"><img loading="lazy" width="1400" height="950" src="'+p+'assets/gallery/spotkanie_profesjonalna_korekta.webp" alt="Organisational meeting">'
 top+='<div><p class="showcase-eyebrow">OPERATIONS / EDUCATION</p><h2>'+('Ideas need<br>execution.' if not pl else 'Idee wymagają<br>działania.')+'</h2><p>'+('My work also includes project creation, operations and developing services and professional education. DBA studies are ongoing, not a completed degree.' if not pl else 'Moja praca obejmuje tworzenie projektów, zarządzanie operacyjne i rozwój usług oraz edukacji. Studia DBA są w toku, nie są ukończonym stopniem.')+'</p><div class="showcase-cta"><a href="'+p+routes[lang]['media']+'">'+('Media archive ↗' if not pl else 'Archiwum mediów ↗')+'</a></div></div></div></div></section>'
 base(lang,'leadership','Leadership & Organisations' if not pl else 'Organizacje i przywództwo',
 'Professional education, organisational leadership, business development and counselling.',top)
def media_page(lang):
 pl=lang=='pl';p=prefix(lang)
 body=hero(lang,'DKK / BROADCASTS · INTERVIEWS · PUBLIC ENGAGEMENT' if not pl else 'DKK / TELEWIZJA · WYWIADY · WYSTĄPIENIA',
 'On the<br><em>record.</em>' if not pl else 'W przestrzeni<br><em>publicznej.</em>',
 'Independent reporting, expert commentary, interviews and education from the archive.' if not pl else 'Niezależne reportaże, wypowiedzi eksperckie, wywiady i materiały edukacyjne.',f'{len(media):02} / MEDIA')
 cards=''
 for m in [x for x in media if x.get('featured')]:
  cards+=f'''<a class="showcase-media-card" href="{e(m['url'],quote=True)}" target="_blank" rel="noopener noreferrer">
<div class="showcase-media-card__image"><img loading="lazy" src="{p+e(m['photo'])}" width="1400" height="1050" alt="{e(m['publisher'])} / archival still"></div>
<div class="showcase-media-card__copy"><span class="showcase-media-card__meta">{e(m['publisher'])} / {m['date'][:4]}</span>
<h3>{e(m['title'][lang])}</h3><p>{e(m['summary'][lang])}</p></div></a>'''
 body+='<section class="showcase-section" id="collection"><div class="container">'+section_head(lang,'01 / SELECTED COVERAGE',
    'Featured<br><em>references.</em>' if not pl else 'Ważne<br><em>materiały.</em>',
    'Links open their original broadcaster, publisher or archival pages.' if not pl else 'Linki prowadzą do oryginalnych stron nadawców, wydawców lub archiwów.')+'<div class="showcase-media-featured">'+cards+'</div></div></section>'
 cats=['all','television','radio','interview','speaking','education','projects','podcast','writing']
 labels_en={'all':'All','television':'Television','radio':'Radio','interview':'Interview','speaking':'Speaking','education':'Education','projects':'Projects','podcast':'Podcast','writing':'Writing'}
 labels_pl={'all':'Wszystkie','television':'Telewizja','radio':'Radio','interview':'Wywiad','speaking':'Wystąpienia','education':'Edukacja','projects':'Projekty','podcast':'Podcast','writing':'Teksty'}
 labels=labels_pl if pl else labels_en
 filters=''.join(f'<button type="button" data-archive-filter="{x}" aria-pressed="{str(x=="all").lower()}">{labels[x]}</button>' for x in cats)
 archive=''
 for m in sorted(media,key=lambda x:x['date'],reverse=True):
  archive+=f'''<a data-archive-card="{e(m['category'])}" href="{e(m['url'],quote=True)}" target="_blank" rel="noopener noreferrer">
<span class="showcase-archive__year">{m['date'][:4]}</span>
<div class="showcase-archive__body"><strong>{e(m['title'][lang])}</strong><small>{e(m['publisher'])} / {labels[m['category']]}</small>
<p>{e(m['summary'][lang])}</p></div><span aria-hidden="true">↗</span></a>'''
 body+='<section class="showcase-section showcase-section--deep"><div class="container">'+section_head(lang,'02 / SOURCE ARCHIVE',
   'Original<br><em>sources.</em>' if not pl else 'Oryginalne<br><em>źródła.</em>',f'{len(media)} '+('selected references' if not pl else 'wybranych odnośników'))
 body+='<div class="showcase-filterbar" role="group" aria-label="Media categories">'+filters+'</div><p class="showcase-eyebrow"><span data-media-counter>'+str(len(media)).zfill(2)+'</span> '+('references' if not pl else 'źródeł')+'</p>'
 body+='<div class="showcase-archive">'+archive+'</div><p class="showcase-gallery-note">'+e(w[lang]['media_caption'])+'</p></div></section>'
 base(lang,'media','Media & Public Engagement' if not pl else 'Media i działalność publiczna',
 'Television, radio, interviews, educational speaking and community projects.',body)
def gallery_page(lang):
 pl=lang=='pl';p=prefix(lang)
 labels_en={'all':'All','media':'Media','speaking':'Speaking','community':'Community','leadership':'Leadership','personal':'Personal','editorial':'Editorial'}
 labels_pl={'all':'Wszystkie','media':'Media','speaking':'Wystąpienia','community':'Społecznie','leadership':'Organizacje','personal':'Prywatnie','editorial':'Redakcyjne'}
 labels=labels_pl if pl else labels_en
 body=hero(lang,'DKK / DOCUMENTARY PHOTOGRAPHY' if not pl else 'DKK / ARCHIWUM FOTOGRAFICZNE',
    'The work<br><em>in pictures.</em>' if not pl else 'Moja praca<br><em>na zdjęciach.</em>',
    'Lectures, interviews, community work, projects and personal moments in one visual archive.' if not pl else 'Wykłady, wywiady, działania społeczne, projekty i codzienność w jednym archiwum.',f'{len(gallery):02} / IMAGES')
 categories=list(labels)
 filters=''.join(f'<button type="button" data-gallery-filter="{x}" aria-pressed="{str(x=="all").lower()}">{labels[x]}</button>' for x in categories)
 figures=''
 for x in gallery:
  name=e(x['title'][lang],quote=True);category=labels[x['category']]
  note=(' / EDITED COMPOSITION' if not pl else ' / KOMPOZYCJA REDAKCYJNA') if x.get('editorial') else ''
  figures+=f'''<figure class="showcase-photo" data-gallery-item="{e(x['category'])}">
<a href="{p+e(x['original'])}" data-gallery-open="{p+e(x['image'])}" data-title="{name}" data-alt="{name}" data-section="{e(category+note)}">
<img src="{p+e(x['image'])}" loading="lazy" width="{x['width']}" height="{x['height']}" alt="{name}"></a>
<figcaption><small>{e(category+note)}</small>{e(x['title'][lang])}</figcaption></figure>'''
 body+='<section class="showcase-section" id="collection"><div class="container">'+section_head(lang,'01 / ARCHIVE',
  'A visual<br><em>record.</em>' if not pl else 'Zapisane<br><em>momenty.</em>',
  str(len(gallery))+(' photographs, grouped by context.' if not pl else ' zdjęć, uporządkowanych tematycznie.'))
 body+='<div class="showcase-filterbar" role="group" aria-label="Photo categories">'+filters+'</div><p class="showcase-eyebrow"><span data-gallery-count>'+str(len(gallery)).zfill(2)+'</span> '+('photographs' if not pl else 'zdjęć')+'</p>'
 body+='<div class="showcase-photo-grid" data-gallery-list>'+figures+'</div><p class="showcase-gallery-note">'+e(w[lang]['gallery_caption'])+'</p></div></section>'
 body+='''<dialog class="showcase-modal" id="photo-viewer" aria-labelledby="photo-view-title"><div class="showcase-modal__top">
<strong id="photo-view-title" data-photo-title>Photograph</strong><button type="button" data-gallery-close aria-label="Close">×</button>
</div><img data-photo-full alt=""><p class="showcase-modal__bottom" data-photo-label></p></dialog>'''
 base(lang,'gallery','Photography & Archive' if not pl else 'Galeria fotografii',
 'Photographs of speaking, teaching, media work, education and professional leadership.',body)
def main():
 for lang in ('en','pl'):leadership(lang);media_page(lang);gallery_page(lang)
 print('Generated bilingual leadership, media and photo gallery pages: 6 total')
if __name__=='__main__':main()
