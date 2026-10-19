#!/usr/bin/env python3
"""Final editorial layer; run after build.py, before deploying GitHub Pages.
Stable page composition + navigation in EN/PL, no third-party build framework.
"""
from pathlib import Path
from html import escape as e
import json,re
R=Path(__file__).resolve().parents[1]
roles=json.loads((R/'data/leadership.json').read_text('utf-8'))
ROUTES={'en':{'home':'index.html','books':'publications/','leader':'leadership/','media':'media/','gallery':'gallery/'},
        'pl':{'home':'pl/index.html','books':'pl/publikacje/','leader':'pl/organizacje/','media':'pl/media/','gallery':'pl/galeria/'}}
LABELS={'en':{'home':'About','books':'Publications','leader':'Leadership','media':'Media','gallery':'Gallery'},
        'pl':{'home':'O mnie','books':'Publikacje','leader':'Organizacje','media':'Media','gallery':'Galeria'}}
def prefix(path):
 return '../'*len(path.parent.parts) if path.parent!=Path('.') else ''
def route(path,lang,key):return prefix(path)+ROUTES[lang][key]
def nav(path,lang):
 return ''.join(f'<a href="{route(path,lang,k)+("#about" if k=="home" else "")}">{LABELS[lang][k]}</a>'
                for k in ('home','leader','books','media','gallery'))
def switch(path,lang):
 name=path.as_posix();pre=prefix(path);other='pl' if lang=='en' else 'en'
 mapping={'leadership/index.html':'pl/organizacje/','pl/organizacje/index.html':'leadership/',
          'media/index.html':'pl/media/','pl/media/index.html':'media/',
          'gallery/index.html':'pl/galeria/','pl/galeria/index.html':'gallery/',
          'publications/index.html':'pl/publikacje/','pl/publikacje/index.html':'publications/'}
 if name in mapping:return pre+mapping[name]
 if name.startswith('works/'):return pre+'pl/publikacje/'+path.parts[1]+'/'
 if name.startswith('pl/publikacje/') and len(path.parts)>3:return pre+'works/'+path.parts[2]+'/'
 return pre+ROUTES[other]['home']
def replace_section(source,pattern,replacement):
 source,num=re.subn(pattern,lambda _:replacement,source,count=1,flags=re.S)
 if num!=1:raise ValueError('Section missing: '+pattern[:75])
 return source
def featured_media(lang,pre):
 pl=lang=='pl'
 return f'''<section class="dkk-home-feature" id="media-highlight"><div class="container dkk-home-feature__grid">
<div class="dkk-home-feature__text"><p class="eyebrow reveal">04 / {'MEDIA & PUBLIC CONVERSATIONS' if not pl else 'MEDIA I WYPOWIEDZI PUBLICZNE'}</p>
<h2 class="reveal">{'On the<br><em>record.</em>' if not pl else 'W centrum<br><em>rozmowy.</em>'}</h2>
<p class="reveal">{'Television appearances, broadcast interviews and expert commentary are part of my public work. The archive links to original reporting and gives each appearance its context.' if not pl else 'Wystąpienia telewizyjne, wywiady i wypowiedzi eksperckie stanowią część mojej działalności publicznej. Archiwum prowadzi do oryginalnych materiałów i objaśnia ich kontekst.'}</p>
<a class="dkk-home-link reveal" href="{pre+ROUTES[lang]['media']}">{'Explore the media archive' if not pl else 'Przeglądaj archiwum mediów'} ↗</a></div>
<div class="dkk-home-feature__photos reveal">
<img loading="lazy" width="1400" height="1050" src="{pre}assets/gallery/16.webp" alt="Dawid Karol Kołodziej in a television studio">
<img loading="lazy" width="1400" height="1050" src="{pre}assets/gallery/17.webp" alt="Professional interview recorded on camera"></div>
</div></section>'''
def roles_section(lang,pre):
 pl=lang=='pl'
 cards=''.join(f'''<article class="dkk-role-card reveal"><span>{e(x['title'][lang])} / {x['from']}—</span>
<h3>{e(x['name'])}</h3><p>{e(x['description'][lang])}</p></article>''' for x in roles)
 return f'''<section id="projects" class="chapter project-section"><div class="container">
<div class="section-topline"><p class="eyebrow">06 / {'BUILDING ORGANISATIONS' if not pl else 'BUDOWANIE ORGANIZACJI'}</p><span class="section-index">LEADERSHIP / 03</span></div>
<div class="chapter-header"><h2 class="chapter-title reveal">{'Building<br><em>institutions.</em>' if not pl else 'Budowanie<br><em>instytucji.</em>'}</h2>
<p class="chapter-note reveal">{'Counselling and mental health practice are one part of my work. I also lead organisations, manage projects and develop competency-based education.' if not pl else 'Poradnictwo i zdrowie psychiczne to część mojej działalności. Kieruję również organizacjami, zarządzam projektami i rozwijam programy kształcenia kompetencyjnego.'}</p></div>
<div class="dkk-home-roles">{cards}</div><div class="works-end"><span class="eyebrow">{'GOVERNANCE · STRATEGY · EDUCATION' if not pl else 'ZARZĄDZANIE · STRATEGIA · EDUKACJA'}</span>
<a class="text-link" href="{pre+ROUTES[lang]['leader']}">{'Explore leadership' if not pl else 'Poznaj działalność organizacyjną'} <span class="arrow">↗</span></a></div></div></section>'''
def gallery_section(lang,pre):
 pl=lang=='pl'
 return f'''<section class="dkk-home-feature" id="gallery-highlight"><div class="container dkk-home-feature__grid">
<div class="dkk-home-feature__text"><p class="eyebrow reveal">07 / {'TEACHING & PHOTOGRAPHY' if not pl else 'WYKŁADY I FOTOGRAFIA'}</p>
<h2 class="reveal">{'The work,<br><em>in pictures.</em>' if not pl else 'Dorobek<br><em>na zdjęciach.</em>'}</h2>
<p class="reveal">{'Training rooms, lectures, interviews, public events and organisational meetings — a documentary archive rather than stock photography.' if not pl else 'Sale szkoleniowe, wykłady, wywiady, wydarzenia i spotkania organizacyjne — fotograficzne archiwum, nie zdjęcia stockowe.'}</p>
<a class="dkk-home-link reveal" href="{pre+ROUTES[lang]['gallery']}">{'Open the complete gallery' if not pl else 'Otwórz pełną galerię'} ↗</a></div>
<div class="dkk-home-feature__photos reveal"><img loading="lazy" width="1400" height="1050" src="{pre}assets/gallery/1.webp" alt="Public training session">
<img loading="lazy" width="1400" height="1050" src="{pre}assets/gallery/21.webp" alt="Presentation at a professional event"></div></div></section>'''
def about_section(lang,pre):
 pl=lang=='pl'
 a=('I began my first placements in charitable organisations in 2009. From 2013, I developed a professional practice in counselling, psychotherapy and psychosocial support. Today my mental health work is based in Queensland, Australia.',
    'My background includes two master’s degrees, in forensic and penitentiary psychology and in a programme focused on personal and career counselling, and a bachelor’s degree in resocialisation and social prophylaxis. I am a PACFA Clinical Registrant. Alongside clinical work, I create projects and lead organisations in counselling and education.') if not pl else (
    'Pierwsze praktyki w organizacjach charytatywnych rozpocząłem w 2009 roku. Od 2013 roku rozwijałem praktykę zawodową w poradnictwie, psychoterapii i wsparciu psychospołecznym. Obecnie pracuję w sektorze zdrowia psychicznego w Queensland w Australii.',
    'Mam dwa tytuły magistra — z psychologii sądowej i penitencjarnej oraz kierunku związanego z poradnictwem osobistym i zawodowym — a także licencjat z resocjalizacji i profilaktyki społecznej. Posiadam status PACFA Clinical Registrant. Równolegle tworzę projekty i kieruję organizacjami w poradnictwie i edukacji.')
 return f'''<section id="about" class="about-section"><div class="container about-grid">
<div class="about-visual reveal"><img class="about-img" src="{pre}assets/gallery/12.webp" loading="lazy" width="1400" height="1050" alt="Radio interview with Dawid Karol Kołodziej">
<div class="about-caption"><span>{'O MNIE / DKK' if pl else 'ABOUT / DKK'}</span><strong>{'PRACTICE & INITIATIVE' if not pl else 'PRAKTYKA I INICJATYWA'}</strong></div></div>
<div class="about-copy"><p class="eyebrow reveal">02 / {'PROFESSIONAL IDENTITY' if not pl else 'PROFIL ZAWODOWY'}</p>
<h2 class="reveal">{'More than<br><em>one role.</em>' if not pl else 'Więcej niż<br><em>jedna rola.</em>'}</h2>
<p class="lead reveal">{'Australia-based psychotherapist offering online consultations, mental health clinician, author and organisational leader.' if not pl else 'Australijski psychoterapeuta prowadzący również konsultacje online, specjalista zdrowia psychicznego, autor i lider organizacji.'}</p>
<p class="reveal">{e(a[0])}</p><p class="reveal">{e(a[1])}</p>
<a class="text-link reveal" href="{pre+ROUTES[lang]['leader']}">{'Organisations and projects' if not pl else 'Organizacje i projekty'} <span class="arrow">↗</span></a></div></div></section>'''
def timeline_section(lang):
 pl=lang=='pl'
 years=[
 ('2009','Early charity placements','Pierwsze praktyki charytatywne','Initial placements in community and charitable organisations, before later professional qualifications.','Praktyki w organizacjach charytatywnych i społecznych przed uzyskaniem późniejszych kwalifikacji.'),
 ('2013','Professional counselling practice','Praktyka zawodowa w poradnictwie','Counselling, psychotherapy and psychosocial support work develops as a professional practice.','Rozwój pracy w poradnictwie, psychoterapii i wsparciu psychospołecznym.'),
 ('2015','President — Psychopedagogical Association','Prezes — Towarzystwo Psychopedagogiczne','Leadership and development of specialist education and support initiatives.','Kierowanie organizacją, rozwój inicjatyw edukacyjnych i pomocowych.'),
 ('2019','Business and operations','Biznes i zarządzanie','Additional operational and organisational work in business and technology.','Poszerzenie działalności o zarządzanie operacyjne i organizacyjne w biznesie oraz technologiach.'),
 ('2024','Australia & association leadership','Australia i kierowanie stowarzyszeniem','Mental health work in Queensland and leadership within the Psychology Counselling Association.','Praca w obszarze zdrowia psychicznego w Queensland i kierowanie Psychology Counselling Association.'),
 ('2025','Headspace Mackay & academic direction','Headspace Mackay i dyrekcja akademicka','Senior mental health role and academic direction of the International Counselling Institute.','Praca specjalistyczna oraz kierowanie sprawami akademickimi International Counselling Institute.'),
 ('2026','Writing, research and business development','Publikacje, badania i rozwój biznesowy','Published articles, working papers and further study in business administration.','Publikacje, opracowania badawcze oraz kontynuowane studia z zarządzania.')
 ]
 rows=''.join(f'<div class="timeline-row reveal"><span class="timeline-year">{y}</span><div><h3>{e(pn if pl else en)}</h3><p>{e(pd if pl else ed)}</p></div></div>' for y,en,pn,ed,pd in years)
 return f'''<section id="journey" class="chapter journey-section"><div class="container">
<div class="section-topline"><p class="eyebrow">05 / {'MILESTONES' if not pl else 'ETAPY ROZWOJU'}</p><span class="section-index">2009—2026</span></div>
<div class="journey-grid"><div><h2 class="chapter-title reveal">{'How the work<br><em>developed.</em>' if not pl else 'Jak rozwijała się<br><em>moja praca.</em>'}</h2>
<p class="dkk-timeline-note">{'The 2009 date identifies early placements, not a claim to qualifications earned later.' if not pl else 'Rok 2009 dotyczy pierwszych praktyk, nie uzyskanych w późniejszych latach kwalifikacji.'}</p></div><div class="timeline">{rows}</div></div></div></section>'''
def hero_section(lang,pre):
 pl=lang=='pl'
 intro=('I work in mental health, write about psychology and education, and build organisations and professional programmes. This is where those areas of my work come together.' if not pl else
        'Pracuję w obszarze zdrowia psychicznego, publikuję teksty o psychologii i edukacji oraz buduję organizacje i programy zawodowe. Ta strona łączy te obszary mojej pracy.')
 return f'''<section class="hero" aria-labelledby="hero-title"><div class="container hero-grid"><div class="hero-copy">
<p class="eyebrow hero-kicker reveal">{'MENTAL HEALTH · EDUCATION · LEADERSHIP' if not pl else 'ZDROWIE PSYCHICZNE · EDUKACJA · PRZYWÓDZTWO'}</p>
<h1 class="reveal" id="hero-title">Dawid Karol<br><em>Kołodziej.</em></h1>
<div class="hero-intro reveal"><p>{e(intro)}</p><a class="text-link" href="#selected">{'Explore the work' if not pl else 'Poznaj dorobek'} <span class="arrow">↗</span></a></div></div>
<div class="hero-visual reveal"><picture><source srcset="{pre}assets/portraits/hero.webp" type="image/webp">
<img class="hero-photo" src="{pre}assets/DawidKolodziej.png" alt="Dawid Karol Kołodziej — portrait" fetchpriority="high" width="1050" height="1312"></picture>
<div class="hero-visual-note"><strong class="eyebrow">DAWID KAROL KOŁODZIEJ</strong><span>QUEENSLAND · AUSTRALIA</span></div><span class="vertical-tag">DKK / PERSONAL ARCHIVE</span></div></div>
<div class="container hero-bottom"><span class="eyebrow">{'2009 EARLY CHARITY PLACEMENTS / PROFESSIONAL WORK FROM 2013' if not pl else '2009 PIERWSZE PRAKTYKI SPOŁECZNE / PRACA ZAWODOWA OD 2013'}</span><span class="eyebrow">{'PRZEWIŃ, ABY ODKRYĆ WIĘCEJ' if pl else 'SCROLL TO EXPLORE'} ↓</span></div></section>'''
def section_replace(src,sel,new):
 patt=(r'<section id="'+sel[3:]+r'"[^>]*>[\s\S]*?</section>') if sel.startswith('id:') else (r'<section class="'+sel+r'"[^>]*>[\s\S]*?</section>')
 out,n=re.subn(patt,lambda m:new,src,count=1)
 if n==0:raise RuntimeError('Missing section: '+sel)
 return out
def update():
 all_pages=[Path('index.html'),Path('pl/index.html'),Path('publications/index.html'),Path('pl/publikacje/index.html')]
 all_pages += [p.relative_to(R) for p in R.glob('works/*/index.html')]
 all_pages += [p.relative_to(R) for p in R.glob('pl/publikacje/*/index.html')]
 for path in all_pages:
  lang='pl' if path.parts[0]=='pl' else 'en';pre=prefix(path);source=(R/path).read_text('utf-8');n=nav(path,lang)
  for classname in ('nav-links','footer-nav'):
   source=re.sub(r'(<nav class="'+classname+r'"[^>]*>)[\s\S]*?(</nav>)',lambda m:m.group(1)+n+m.group(2),source,count=1)
  source=re.sub(r'(<nav aria-label="Mobile navigation">)[\s\S]*?(</nav>)',lambda m:m.group(1)+n+m.group(2),source,count=1)
  alt=switch(path,lang)
  source=re.sub(r'<a class="locale-link"[^>]*>[\s\S]*?</a>',f'<a class="locale-link" lang="{"pl" if lang=="en" else "en"}" href="{e(alt)}">{"PL" if lang=="en" else "EN"} ↗</a>',source,count=1)
  if 'css/showcase.css' not in source:source=source.replace('</head>',f'<link rel="stylesheet" href="{pre}css/showcase.css"><script defer src="{pre}js/showcase.js"></script></head>',1)
  if path.as_posix() in ('index.html','pl/index.html'):
   source=section_replace(source,'hero',hero_section(lang,pre))
   source=section_replace(source,'id:about',about_section(lang,pre))
   source=section_replace(source,'film-section',featured_media(lang,pre))
   source=section_replace(source,'id:journey',timeline_section(lang))
   source=section_replace(source,'id:projects',roles_section(lang,pre))
   source=section_replace(source,'id:credentials',gallery_section(lang,pre))
   source=section_replace(source,'id:library','')
   source=re.sub(r'<meta property="og:image" content="[^"]*">','<meta property="og:image" content="https://dkk.hqici.com/assets/DawidKolodziej.png">',source,count=1)
  (R/path).write_text(source,'utf-8')
 print('Updated',len(all_pages),'existing pages with bilingual navigation and editorial homepage.')
if __name__=='__main__':update()
