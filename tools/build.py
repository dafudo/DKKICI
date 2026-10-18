#!/usr/bin/env python3
"""Rebuild static bilingual HTML from JSON. Python stdlib only; no framework or Node."""
from __future__ import annotations
import html
import json
from pathlib import Path
from urllib.parse import quote, urlsplit, parse_qs
import re
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / 'data/publications.json').read_text(encoding='utf-8'))
S = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
assert isinstance(P, list) and all(isinstance(x, dict) for x in P)
assert len(set(x['slug'] for x in P)) == len(P), 'Slugs must be unique'
for x in P:
    assert x['slug'].replace('-','').isalnum() and x['slug'] == x['slug'].lower(), 'Invalid slug'
    assert x['status'] in ('preview', 'published', 'archived')
    assert x['kind'] in ('book','journal','essay','resource')
    assert x['category'] in ('psychology','education','practice','ideas')
    assert len(x['date']) == 10
    assert all(isinstance(x[k],dict) and x[k].get('en') and x[k].get('pl') for k in ['title','subtitle','description'])
    assert x['cover'].startswith('assets/') and (ROOT / x['cover']).is_file(), f'Missing cover: {x["cover"]}'
P.sort(key=lambda x: x['date'], reverse=True)

I = {
'en': dict(lang='en', home='Home', work='Selected work', about='About', archive='Publications', connect='Connect',
 heroK='PSYCHOTHERAPY · WRITING · EDUCATION', hero='<span>Beyond</span><br>the <em>obvious.</em>',
 heroInfo='A personal archive of people, ideas and the work that connects them. From Poland to Australia, and always in progress.',
 seeWork='Explore the work', chapter1='01 — SELECTED WORK', workH='A collection of<br><em>curiosities.</em>',
 workNote='Books, editorial projects, essays and practical ideas. Different formats. One ongoing conversation.',
 viewAll='Explore full archive', curation='Curated selections / an evolving library',
 chapter2='02 — THE PERSON', aboutH='More than<br><em>a title.</em>',
 aboutLead='I work at the meeting point of mental health, psychotherapy, education and writing.',
 aboutA='My professional path began in Poland and continued in Australia. Along the way, I have worked with young people, adults and families, supported learning, and built projects around psychological knowledge.',
 aboutB='This space is a place for the work itself: what I write, what I question, what I build, and the ideas I want to share. The portrait and text are introductory and can be expanded with your own story.',
 storyLink='Follow the journey', place='POLAND / AUSTRALIA',
 quoteEyebrow='03 — A WAY OF THINKING', quote='Good questions make<br><em>room for better answers.</em>', quoteBy='A thought behind this archive — editable editorial copy',
 filmEyebrow='04 — IN MOTION', filmTitle='The story<br><em>in motion.</em>', filmText='A short personal film will live here. For now, explore the creative direction of the sequence.', filmBtn='View film concept', filmLabel='PERSONAL FILM / PLACEHOLDER',
 journeyK='05 — EXPERIENCE', journeyH='A path,<br><em>not a list.</em>',
 projK='06 — INITIATIVES', projH='Work that<br><em>keeps growing.</em>', projNote='A few of the organisations and initiatives connected to this story.',
 archiveK='07 — THE LIBRARY', archiveH='A living<br><em>archive.</em>', archiveNote='Explore the growing collection. Search across titles and topics, or filter by subject.',
 filterAll='All', filterPsych='Psychology', filterEdu='Education', filterPractice='Practice', filterIdeas='Ideas', search='Search the archive…', countLabel='WORKS IN VIEW', empty='No works match your search. Try another keyword or filter.',
 connectK='08 — CONTACT', connectH='Every story<br>begins with <em>a conversation.</em>', connectP='For professional collaborations, writing and educational projects. A place for considered conversations and new perspectives.', connectBtn='Send an email', connectPending='CONTACT CHANNEL — TO BE ADDED',
 footerSub='Personal archive · psychotherapy · writing · education', made='INDEPENDENT DIGITAL ARCHIVE', top='Back to top',
 preview='Editorial preview', detailBack='Back to the library', published='Year', type='Format', subject='Subject',
 share='Copy page link', copied='Link copied', unavailable='Copy unavailable', publishedLabel='Published',
 previewNote='This is an editorial demonstration. Confirm the bibliographic details, authorship and links before removing the preview status.',
 noLinks='Publication links will be added after verification.', otherH='More to explore',
 filmModalK='A FILM TO BE MADE', filmModalH='A portrait in motion.', filmModalText='Storyboard: a quiet opening portrait, scenes from writing and everyday work, a short direct-to-camera introduction, followed by an understated end title. To activate the film, add a video URL in data/site.json (videoUrl) and rebuild the pages.',
 filmClose='Close', poster='PORTRAIT PLACEHOLDER', edit='REPLACE WITH YOUR PHOTO', read='Read online', view='Open publication', draft='Preview / details to verify',
 typeLabels={'book':'Book','journal':'Journal','essay':'Essay','resource':'Resource'},
 categoryLabels={'psychology':'Psychology','education':'Education','practice':'Practice','ideas':'Ideas'},
 events=[('2013','The beginning','Early work in counselling, psychological and educational support.'),('2015','Building an organisation','Beginning of leadership at Towarzystwo Psychopedagogiczne.'),('2024','A new chapter in Australia','Continued practice in youth mental health and counselling in Queensland.'),('2026','Writing and learning','An expanding catalogue of publications and continuing professional development.')],
 projects=[('01','Towarzystwo Psychopedagogiczne','Leadership, interdisciplinary collaboration and psychological education.'),('02','MENTE','A publication space for ideas about psychology, education and contemporary life.'),('03','ICI and educational projects','Learning resources and initiatives designed to bring practical knowledge closer to people.')],
 ),
'pl': dict(lang='pl', home='Start', work='Wybrane prace', about='O mnie', archive='Publikacje', connect='Kontakt',
 heroK='PSYCHOTERAPIA · PISANIE · EDUKACJA', hero='<span>Poza</span><br><em>schematem.</em>',
 heroInfo='Osobiste archiwum ludzi, idei i pracy, która je łączy. Od Polski po Australię — w nieustannym rozwoju.',
 seeWork='Poznaj dorobek', chapter1='01 — WYBRANE PRACE', workH='Kolekcja<br><em>ciekawości.</em>',
 workNote='Książki, projekty redakcyjne, eseje i praktyczne idee. Różne formy, jedna niekończąca się rozmowa.',
 viewAll='Zobacz całe archiwum', curation='Wybrane publikacje / żywe archiwum',
 chapter2='02 — CZŁOWIEK', aboutH='Więcej niż<br><em>tytuł.</em>',
 aboutLead='Pracuję na styku zdrowia psychicznego, psychoterapii, edukacji i pisania.',
 aboutA='Moja droga zawodowa rozpoczęła się w Polsce, a następnie zaprowadziła mnie do Australii. Pracowałem z młodymi ludźmi, dorosłymi i rodzinami, wspierałem procesy uczenia się i rozwijałem inicjatywy związane z wiedzą psychologiczną.',
 aboutB='Ta strona ma przede wszystkim prezentować moje prace: to, co piszę, co kwestionuję, co buduję i czym chcę się dzielić. To wstępna wersja biografii, którą uzupełnimy autorską historią.',
 storyLink='Moja droga', place='POLSKA / AUSTRALIA',
 quoteEyebrow='03 — SPOSÓB MYŚLENIA', quote='Dobre pytania tworzą<br><em>miejsce na lepsze odpowiedzi.</em>', quoteBy='Myśl przewodnia archiwum — tekst redakcyjny do autoryzacji',
 filmEyebrow='04 — W RUCHU', filmTitle='Historia<br><em>w ruchu.</em>', filmText='Tutaj znajdzie się krótki autorski film. Na razie zobacz proponowaną koncepcję ujęć.', filmBtn='Zobacz koncepcję', filmLabel='FILM OSOBISTY / PLACEHOLDER',
 journeyK='05 — DOŚWIADCZENIE', journeyH='Droga,<br><em>nie lista.</em>',
 projK='06 — INICJATYWY', projH='Projekty, które<br><em>rosną.</em>', projNote='Wybrane organizacje i inicjatywy związane z moją działalnością.',
 archiveK='07 — BIBLIOTEKA', archiveH='Żywe<br><em>archiwum.</em>', archiveNote='Przeglądaj zbiór publikacji. Wyszukuj tytuły i zagadnienia albo filtruj według dziedziny.',
 filterAll='Wszystkie', filterPsych='Psychologia', filterEdu='Edukacja', filterPractice='Praktyka', filterIdeas='Idee', search='Szukaj w bibliotece…', countLabel='WIDOCZNE POZYCJE', empty='Brak publikacji spełniających kryteria. Zmień wyszukiwanie lub filtr.',
 connectK='08 — KONTAKT', connectH='Każda historia<br>zaczyna się od <em>rozmowy.</em>', connectP='W sprawie współpracy zawodowej, publikacji i projektów edukacyjnych. Przestrzeń dla wartościowych rozmów i nowych perspektyw.', connectBtn='Napisz wiadomość', connectPending='KANAŁ KONTAKTOWY — DO UZUPEŁNIENIA',
 footerSub='Archiwum osobiste · psychoterapia · pisanie · edukacja', made='NIEZALEŻNE ARCHIWUM CYFROWE', top='Do góry',
 preview='Wersja demonstracyjna', detailBack='Wróć do biblioteki', published='Rok', type='Forma', subject='Tematyka',
 share='Kopiuj link', copied='Link skopiowany', unavailable='Kopiowanie niedostępne', publishedLabel='Opublikowano',
 previewNote='To demonstracyjna prezentacja. Przed usunięciem statusu podglądu zweryfikuj dane wydawnicze, autorstwo i linki.',
 noLinks='Linki do publikacji zostaną uzupełnione po weryfikacji.', otherH='Odkryj więcej',
 filmModalK='FILM DO NAGRANIA', filmModalH='Portret w ruchu.', filmModalText='Scenariusz: spokojny kadr portretowy, sceny pisania i codziennej pracy, krótka wypowiedź do kamery oraz oszczędna plansza końcowa. Aby uruchomić film, dodaj adres pliku w data/site.json (videoUrl) i przebuduj strony.',
 filmClose='Zamknij', poster='MIEJSCE NA PORTRET', edit='TUTAJ DODAMY TWOJE ZDJĘCIE', read='Czytaj online', view='Otwórz publikację', draft='Podgląd / dane do weryfikacji',
 typeLabels={'book':'Książka','journal':'Czasopismo','essay':'Esej','resource':'Materiał'},
 categoryLabels={'psychology':'Psychologia','education':'Edukacja','practice':'Praktyka','ideas':'Idee'},
 events=[('2013','Początek praktyki','Pierwsze działania w obszarze poradnictwa oraz wsparcia psychologiczno-edukacyjnego.'),('2015','Budowanie organizacji','Początek kierowania Towarzystwem Psychopedagogicznym.'),('2024','Nowy rozdział w Australii','Kontynuacja pracy w zakresie zdrowia psychicznego młodzieży i poradnictwa w Queensland.'),('2026','Publikacje i rozwój','Rozbudowa biblioteki publikacji i dalsze doskonalenie zawodowe.')],
 projects=[('01','Towarzystwo Psychopedagogiczne','Przywództwo, współpraca interdyscyplinarna i edukacja psychologiczna.'),('02','MENTE','Przestrzeń publikacji o psychologii, edukacji i współczesnym życiu.'),('03','ICI i projekty edukacyjne','Materiały i inicjatywy służące upowszechnianiu praktycznej wiedzy.')],
 )}

def e(s): return html.escape(str(s),quote=True)
def href_for(pub,lang):
    return ('pl/publikacje/' if lang == 'pl' else 'works/') + quote(pub['slug']) + '/'
def rpath(path,prefix): return prefix+path

def card(pub,lang,prefix,archive=False):
    t=I[lang]; label=e(pub['title'][lang]); desc=e(pub['subtitle'][lang]); img=e(prefix+pub['cover']); url=e(prefix+href_for(pub,lang)); y=e(pub['year']); categ=e(pub['category']); search=e(' '.join([pub['title']['en'],pub['title']['pl'],pub['subtitle']['en'],pub['subtitle']['pl'],pub['description'][lang]]))
    attr = f' data-work-card data-category="{categ}" data-search="{search}"' if archive else ''
    status = f'<span class="work-status">{e(t["preview"])}</span>' if pub['status']!='published' else ''
    return f'''<a class="work-card reveal" href="{url}"{attr} aria-label="{label}"><div class="work-image"><span class="work-image-tag">{e(t['typeLabels'][pub['kind']])} / {y}</span><img src="{img}" alt="{label} — editorial cover mockup" loading="lazy" width="660" height="880"><span class="work-image-arrow" aria-hidden="true">↗</span></div><div class="work-meta"><span>{e(t['categoryLabels'][pub['category']])}</span><span>—</span><span>{y}</span>{status}</div><h3>{label}</h3><p class="work-sub">{desc}</p></a>'''

def header(lang,prefix,detail=False):
    t=I[lang]; root=prefix; home=prefix+('pl/index.html' if lang=='pl' else 'index.html'); rootpl=prefix+'pl/index.html'
    # detail base prefix points to repo root; route switch to corresponding detail page
    alt=(prefix + ('pl/' if lang=='en' else '') + ('publikacje/' if detail and lang=='en' else '')) if False else ''
    target=prefix+('pl/index.html' if lang=='en' else 'index.html')
    if detail:
        slug=detail
        target=prefix+href_for(next(p for p in P if p['slug']==slug),'pl' if lang=='en' else 'en')+'index.html'
    catalogue=prefix+('pl/publikacje/' if lang=='pl' else 'publications/')
    nav=''.join(f'<a href="{e(catalogue if anchor=="library" else home+"#"+anchor)}">{e(t[text])}</a>' for anchor,text in [('selected','work'),('about','about'),('library','archive'),('contact','connect')])
    return f'''<a class="skip" href="#main">Skip to content</a><header class="site-nav"><div class="nav-inner container"><a class="brand" href="{home}" aria-label="{e(S['owner'])} — home"><span class="brand-mark">DKK.</span><span class="brand-caption">PERSONAL / ARCHIVE</span></a><nav class="nav-links" aria-label="Main navigation">{nav}</nav><div class="nav-right"><a class="locale-link" lang="{'pl' if lang=='en' else 'en'}" href="{target}" aria-label="Change language">{'PL' if lang=='en' else 'EN'} <span aria-hidden="true">↗</span></a><button class="nav-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="mobile-nav" aria-label="Menu"><span></span><span></span></button></div></div></header><div class="mobile-panel" id="mobile-nav" aria-hidden="true"><div class="container"><p class="eyebrow">NAVIGATION / MENU</p><nav aria-label="Mobile navigation">{nav}</nav></div></div>'''

def footer(lang,prefix):
    t=I[lang]; home=prefix+('pl/index.html' if lang=='pl' else 'index.html')
    catalogue=prefix+('pl/publikacje/' if lang=='pl' else 'publications/')
    links=''.join(f'<a href="{e(catalogue if anchor=="library" else home+"#"+anchor)}">{e(t[txt])}</a>' for anchor,txt in [('selected','work'),('about','about'),('library','archive'),('contact','connect')])
    return f'''<footer class="footer"><div class="container"><div class="footer-top"><a href="{home}" class="footer-brand">DKK.</a><nav class="footer-nav" aria-label="Footer navigation">{links}</nav></div><div class="footer-bottom"><span>© {e(S['owner'])} · {e(t['made'])}</span><a href="#top">↑ {e(t['top'])}</a></div></div></footer>'''

def shell(lang,title,description,prefix,body,detail=False):
    t=I[lang]
    # noindex until demo content and portrait are replaced, intentionally
    titlefull=e(title)+' — '+e(S['owner']); desc=e(description)
    detail_assets=f'<link rel="stylesheet" href="{e(prefix+"css/publications.css")}">' if detail else ''
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="theme-color" content="#202624"><meta name="robots" content="noindex,nofollow"><meta name="description" content="{desc}"><meta property="og:title" content="{titlefull}"><meta property="og:description" content="{desc}"><meta property="og:type" content="{'article' if detail else 'website'}"><meta property="og:image" content="{e(prefix+'assets/cover-motivation.svg')}"><title>{titlefull}</title><link rel="icon" type="image/svg+xml" href="{e(prefix+'assets/favicon.svg')}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="preconnect" href="https://images.unsplash.com"><script>document.documentElement.classList.add('js')</script><link rel="stylesheet" href="{e(prefix+'css/style.css')}">{detail_assets}<script defer src="{e(prefix+'js/main.js')}"></script></head><body id="top" class="{'detail-page' if detail else 'home-page'}">{header(lang,prefix,detail)}{body}{footer(lang,prefix)}</body></html>'''

def home_page(lang,prefix):
    t=I[lang]
    catalog_url=prefix+('pl/publikacje/' if lang=='pl' else 'publications/')
    cover=S['portrait'] or 'assets/portrait-placeholder.svg'
    about_image=S['aboutPortrait'] or S['stockPhotoJournal']
    filmUrl=S.get('videoUrl','').strip()
    hero_cards=''.join(card(p,lang,prefix) for p in [p for p in P if p.get('featured') and p['status']!='archived'][:3])
    all_cards=''.join(card(p,lang,prefix) for p in [p for p in P if p['status']!='archived'][:3])
    options=''.join(f'<button class="filter" type="button" data-filter="{v}" aria-pressed="{str(i==0).lower()}">{e(t[k])}</button>' for i,(v,k) in enumerate([('all','filterAll'),('psychology','filterPsych'),('education','filterEdu'),('practice','filterPractice'),('ideas','filterIdeas')]))
    timeline=''.join(f'<div class="timeline-row reveal"><span class="timeline-year">{e(year)}</span><div><h3>{e(h)}</h3><p>{e(d)}</p></div></div>' for year,h,d in t['events'])
    projects=''.join(f'<article class="project-item reveal"><span class="project-no">PROJECT / {e(n)}</span><div><h3>{e(h)}</h3><p>{e(d)}</p></div></article>' for n,h,d in t['projects'])
    video = f'<p>{e(t["filmModalText"])}</p>'
    if filmUrl.startswith('https://'):
        parts = urlsplit(filmUrl)
        yid = ''
        if parts.hostname in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            yid = parse_qs(parts.query).get('v',[''])[0] if parts.path == '/watch' else (parts.path.split('/embed/')[-1] if '/embed/' in parts.path else '')
        elif parts.hostname == 'youtu.be': yid = parts.path.strip('/')
        if re.fullmatch(r'[A-Za-z0-9_-]{11}',yid):
            video = f'<iframe class="modal-video" height="410" loading="lazy" src="https://www.youtube-nocookie.com/embed/{e(yid)}" title="{e(t["filmBtn"])}" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
        elif filmUrl.lower().endswith(('.mp4','.webm')):
            mimetype = 'video/webm' if filmUrl.lower().endswith('.webm') else 'video/mp4'
            video = f'<video class="modal-video" controls preload="none" playsinline><source src="{e(filmUrl)}" type="{mimetype}"></video>'
    contact_button=f'<a class="connect-action" href="mailto:{e(S["email"])}">{e(t["connectBtn"])} <span class="arrow">↗</span></a>' if S['email'] else f'<div class="contact-placeholder">{e(t["connectPending"])}</div>'
    body=f'''
<main id="main">
<section class="hero" aria-labelledby="hero-title"><div class="container hero-grid"><div class="hero-copy"><p class="eyebrow hero-kicker reveal">{e(t['heroK'])}</p><h1 class="reveal" id="hero-title">{t['hero']}</h1><div class="hero-intro reveal"><p>{e(t['heroInfo'])}</p><a class="text-link" href="#selected">{e(t['seeWork'])}<span class="arrow">↗</span></a></div></div><div class="hero-visual reveal"><img class="hero-photo" src="{e(prefix+cover) if not cover.startswith('http') else e(cover)}" width="900" height="1120" alt="Portrait placeholder — replace with personal photography" fetchpriority="high"><div class="hero-visual-note"><strong class="eyebrow">{e(t['poster'])}</strong><span>{e(t['edit'])}</span></div><span class="vertical-tag">DKK — AN INDEPENDENT ARCHIVE</span></div></div><div class="container hero-bottom"><span class="eyebrow">{e(t['place'])}</span><span class="eyebrow">SCROLL TO EXPLORE ↓</span></div></section>
<section id="selected" class="chapter selected-section"><div class="container"><div class="section-topline"><p class="eyebrow">{e(t['chapter1'])}</p><span class="section-index">001 / 008</span></div><div class="chapter-header"><h2 class="chapter-title reveal">{t['workH']}</h2><p class="chapter-note reveal">{e(t['workNote'])}</p></div><div class="featured-grid">{hero_cards}</div><div class="works-end"><span class="eyebrow">{e(t['curation'])}</span><a class="text-link" href="{e(catalog_url)}">{e(t['viewAll'])}<span class="arrow">↗</span></a></div></div></section>
<section id="about" class="about-section"><div class="container about-grid"><div class="about-visual reveal"><img class="about-img about-image-source" src="{e(about_image) if about_image.startswith('http') else e(prefix+about_image)}" data-fallback="{e(prefix+'assets/desk-placeholder.svg')}" loading="lazy" alt="Editorial stock photo placeholder showing a writing desk" width="1100" height="1350"><div class="about-caption"><span>ABOUT / DKK</span><strong>{e(t['place'])}</strong></div></div><div class="about-copy"><p class="eyebrow reveal">{e(t['chapter2'])}</p><h2 class="reveal">{t['aboutH']}</h2><p class="lead reveal">{e(t['aboutLead'])}</p><p class="reveal">{e(t['aboutA'])}</p><p class="reveal">{e(t['aboutB'])}</p><a class="text-link reveal" href="#journey">{e(t['storyLink'])}<span class="arrow">↗</span></a></div></div></section>
<section class="statement" aria-label="Editorial statement"><div class="container statement-inner"><p class="eyebrow reveal">{e(t['quoteEyebrow'])}</p><blockquote class="reveal">{t['quote']}</blockquote><p class="statement-byline reveal">{e(t['quoteBy'])}</p></div></section>
<section class="film-section"><div class="film-shell"><div class="film-overlay reveal"><p class="eyebrow">{e(t['filmEyebrow'])}</p><h2>{t['filmTitle']}</h2><p>{e(t['filmText'])}</p><button class="film-play" type="button" data-open-film aria-label="{e(t['filmBtn'])}"><span aria-hidden="true">▶</span></button><span class="film-label">{e(t['filmLabel'])}</span></div></div></section>
<section id="journey" class="chapter journey-section"><div class="container"><div class="section-topline"><p class="eyebrow">{e(t['journeyK'])}</p><span class="section-index">005 / 008</span></div><div class="journey-grid"><h2 class="chapter-title reveal">{t['journeyH']}</h2><div class="timeline">{timeline}</div></div></div></section>
<section id="projects" class="chapter project-section"><div class="container"><div class="section-topline"><p class="eyebrow">{e(t['projK'])}</p><span class="section-index">006 / 008</span></div><div class="chapter-header"><h2 class="chapter-title reveal">{t['projH']}</h2><p class="chapter-note reveal">{e(t['projNote'])}</p></div><div class="projects-grid">{projects}</div></div></section>
<section id="library" class="chapter archive-section"><div class="container"><div class="section-topline"><p class="eyebrow">{e(t['archiveK'])}</p><span class="section-index">007 / 008</span></div><div class="chapter-header"><h2 class="chapter-title reveal">{t['archiveH']}</h2><p class="chapter-note reveal">{e(t['archiveNote'])}</p></div><div class="archive-grid">{all_cards}</div><div class="works-end"><span class="eyebrow">{e(t['curation'])}</span><a class="text-link" href="{e(catalog_url)}">{e(t['viewAll'])}<span class="arrow">↗</span></a></div></div></section>
<section id="contact" class="connect-section"><div class="container"><p class="eyebrow reveal">{e(t['connectK'])}</p><h2 class="connect-heading reveal">{t['connectH']}</h2><div class="connect-details reveal"><p>{e(t['connectP'])}</p>{contact_button}</div></div></section>
</main><div class="modal" data-film-modal role="dialog" aria-modal="true" aria-hidden="true" aria-labelledby="film-dialog-title"><div class="modal-body"><button class="modal-close" type="button" data-close-film aria-label="{e(t['filmClose'])}">×</button><p class="eyebrow">{e(t['filmModalK'])}</p><h2 id="film-dialog-title">{e(t['filmModalH'])}</h2>{video}</div></div>'''
    return shell(lang,S['owner'],t['heroInfo'],prefix,body)

def detail_page(pub,lang,prefix):
    t=I[lang]; title=pub['title'][lang]; subtitle=pub['subtitle'][lang]
    links=[]
    for l in pub.get('links',[]):
        url=l.get('url',''); name=l.get('label','')
        if url.startswith('https://'):
            links.append(f'<a rel="noopener noreferrer" target="_blank" href="{e(url)}">{e(name)} ↗</a>')
    if pub.get('readUrl','').startswith('https://'): links.insert(0,f'<a rel="noopener noreferrer" target="_blank" href="{e(pub["readUrl"])}">{e(t["read"])} ↗</a>')
    if not links: links.append(f'<p class="muted">{e(t["noLinks"])}</p>')
    others=[p for p in P if p['slug']!=pub['slug'] and p['status']!='archived'][:2]
    extra=''.join(card(p,lang,prefix) for p in others)
    preview=f'<p class="detail-note">{e(t["previewNote"])}</p>' if pub['status']!='published' else ''
    back=prefix+('pl/publikacje/' if lang=='pl' else 'publications/')
    body=f'''<main id="main" class="detail-main"><div class="container"><a class="detail-back" href="{e(back)}">← {e(t['detailBack'])}</a><div class="detail-grid"><div class="detail-copy"><p class="eyebrow accent">{e(t['categoryLabels'][pub['category']])} / {e(t['typeLabels'][pub['kind']])}</p><h1 class="detail-title">{e(title)}</h1><p class="detail-subtitle">{e(subtitle)}</p><p class="detail-summary">{e(pub['description'][lang])}</p><div class="detail-facts"><div><span class="eyebrow">{e(t['published'])}</span><span>{e(pub['year'])}</span></div><div><span class="eyebrow">{e(t['type'])}</span><span>{e(t['typeLabels'][pub['kind']])}</span></div><div><span class="eyebrow">{e(t['subject'])}</span><span>{e(t['categoryLabels'][pub['category']])}</span></div><div><span class="eyebrow">STATUS</span><span>{e(t['preview'] if pub['status']!='published' else t['publishedLabel'])}</span></div></div><div class="detail-actions">{''.join(links)}<button class="secondary" type="button" data-copy-link data-copied="{e(t['copied'])}" data-failed="{e(t['unavailable'])}">{e(t['share'])}</button></div>{preview}</div><div class="detail-cover"><img src="{e(prefix+pub['cover'])}" alt="{e(title)} — editorial cover mockup" width="660" height="880"></div></div><div class="detail-other"><h2>{e(t['otherH'])}</h2><div class="featured-grid">{extra}</div></div></div></main>'''
    return shell(lang,title,pub['description'][lang],prefix,body,detail=pub['slug'])

(ROOT/'index.html').write_text(home_page('en',''),encoding='utf-8')
(ROOT/'pl/index.html').write_text(home_page('pl','../'),encoding='utf-8')
for p in P:
    for lang in ('en','pl'):
        path=ROOT/href_for(p,lang)/'index.html'
        path.parent.mkdir(parents=True,exist_ok=True)
        prefix='../../../' if lang=='pl' else '../../'
        path.write_text(detail_page(p,lang,prefix),encoding='utf-8')
(ROOT/'404.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>404 — DKK.</title><style>body{font-family:Georgia,serif;background:#202624;color:#f3f0e9;display:grid;place-items:center;min-height:100vh;text-align:center}h1{font-size:6rem;font-weight:normal;margin:0}a{color:#c2a57c}</style><main><h1>404.</h1><p>This page could not be found.</p><a href="./index.html">Return to the archive →</a></main></html>''',encoding='utf-8')
(ROOT/'.nojekyll').write_text('',encoding='utf-8')
print(f'Built homepage (EN + PL) and {len(P)*2} publication pages. No external dependencies.')
