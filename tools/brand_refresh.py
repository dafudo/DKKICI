#!/usr/bin/env python3
"""Publish the bilingual professional profile and refresh evergreen identity pages.

This is a post-processing stage: run AFTER build.py, showcase_pages.py,
enrich_home.py and BEFORE localize_english_name.py and generate_sitemap.py.
All copy comes from data/profile.json. Uses Python stdlib only.
"""
from __future__ import annotations
from html import escape as h
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
PROFILE=json.loads((ROOT/'data/profile.json').read_text('utf-8'))
SITE=json.loads((ROOT/'data/site.json').read_text('utf-8'))
PUBLICATIONS=json.loads((ROOT/'data/publications.json').read_text('utf-8'))
ROLES=json.loads((ROOT/'data/leadership.json').read_text('utf-8'))
BASE="https://dkk.hqici.com/"
IDENTIFIERS=[
    ("ORCID", "https://orcid.org/0009-0007-5526-2576"),
    ("Google Scholar", "https://scholar.google.com/citations?hl=en&user=u76jDVcAAAAJ"),
    ("LinkedIn", "https://www.linkedin.com/in/dafudo/"),
]
LANG={
  "en":{"profile":"profile/","home":"index.html","leadership":"leadership/","publications":"publications/","media":"media/","gallery":"gallery/","switch":"pl/profil/","nav":["Profile","Leadership","Publications","Media","Gallery"],"eyebrow":"PROFESSIONAL PROFILE / DKK","story":"An interdisciplinary professional background","role":"Current roles","practice":"Clinical and psychosocial work","identity":"Verified profiles","early":"2009 / EARLY CHARITY PLACEMENTS","period":"2013 / PROFESSIONAL PRACTICE","link":"View full profile","overview":"Professional profile","source":"External professional record","progress":"IN PROGRESS","background":"Background & experience","publicationDate":"Published works"},
  "pl":{"profile":"pl/profil/","home":"pl/index.html","leadership":"pl/organizacje/","publications":"pl/publikacje/","media":"pl/media/","gallery":"pl/galeria/","switch":"profile/","nav":["Profil","Organizacje","Publikacje","Media","Galeria"],"eyebrow":"PROFIL ZAWODOWY / DKK","story":"Interdyscyplinarna droga zawodowa","role":"Obecne funkcje","practice":"Praca i wsparcie psychospołeczne","identity":"Zweryfikuj profile","early":"2009 / PIERWSZE PRAKTYKI SPOŁECZNE","period":"2013 / PRAKTYKA ZAWODOWA","link":"Pełny profil zawodowy","overview":"Profil zawodowy","source":"Zewnętrzne źródła zawodowe","progress":"W TOKU","background":"Doświadczenie zawodowe","publicationDate":"Opublikowane prace"}
}

def js(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('<',r'\u003c').replace('>',r'\u003e')

def relative(path):
    return '../'*len(path.parent.parts) if path.parent!=Path('.') else ''

def href(prefix,lang,key):
    return prefix+LANG[lang][key]

def nav(prefix,lang):
    x=LANG[lang]
    keys=('profile','leadership','publications','media','gallery')
    return ''.join('<a href="'+h(href(prefix,lang,k),quote=True)+'">'+h(label)+'</a>' for k,label in zip(keys,x['nav']))

def link(label,url,cls=''):
    return '<a'+(' class="'+cls+'"' if cls else '')+' href="'+h(url,quote=True)+'" target="_blank" rel="noopener noreferrer">'+h(label)+' <span aria-hidden="true">↗</span></a>'

def block_list(items):
    blocks=[]
    for x in items:
        source=x.get('url','')
        label=x.get('linkLabel','Source')
        more=link(label,source,'p-credential__source') if source.startswith('https://') else ''
        blocks.append('<article class="p-credential"><h3>'+h(x['heading'])+'</h3><p>'+h(x['detail'])+'</p>'+more+'</article>')
    return ''.join(blocks)

def profile_page(lang):
    d=PROFILE[lang];t=LANG[lang];pl=lang=='pl'
    prefix='../' if not pl else '../../'
    pairs=tuple(zip(('profile','leadership','publications','media','gallery'),t['nav']))
    navigation=nav(prefix,lang)
    bio=''.join('<p>'+h(p)+'</p>' for p in d['biography'])
    roles=''.join('<article class="p-role"><span>'+h(r['title'][lang])+' / '+h(r['from'])+'—</span><h3>'+h(r['name'])+'</h3><p>'+h(r['description'][lang])+'</p>'+ (link('Organisation website' if lang=='en' else 'Strona organizacji',r['url'],'p-role__source') if r.get('url','').startswith('https://') else '') + '</article>' for r in ROLES)
    practice=''.join('<li>'+h(v)+'</li>' for v in d['scope'])
    externals=''.join(link(label,url,'p-source') for label,url in IDENTIFIERS)
    intro=(d['subtitle']+'. '+d['intro'])
    title=t['overview']+' — '+d['name']
    canonical=BASE+t['profile']
    photo=BASE+'assets/DawidKolodziej.png'
    markup='''<!doctype html><html lang="'''+lang+'''"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="index,follow"><meta name="color-scheme" content="light"><meta name="theme-color" content="#202824">
<meta name="description" content="'''+h(intro,quote=True)+'''">
<title>'''+h(title)+'''</title><meta property="og:type" content="profile"><meta property="og:title" content="'''+h(title,quote=True)+'''">
<meta property="og:description" content="'''+h(intro,quote=True)+'''"><meta property="og:image" content="'''+photo+'''">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="'''+prefix+'''assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="'''+prefix+'''css/style.css"><link rel="stylesheet" href="'''+prefix+'''css/showcase.css"><link rel="stylesheet" href="'''+prefix+'''css/profile.css">
<script>document.documentElement.classList.add('js')</script><script defer src="'''+prefix+'''js/main.js"></script></head>
<body id="top" class="showcase-page profile-page"><a class="skip" href="#main">'''+('Skip to content' if not pl else 'Przejdź do treści')+'''</a>
<header class="site-nav"><div class="nav-inner container"><a class="brand" href="'''+prefix+t['home']+'''"><span class="brand-mark">DKK.</span><span class="brand-caption">PERSONAL / ARCHIVE</span></a>
<nav class="nav-links" aria-label="Main navigation">'''+navigation+'''</nav><div class="nav-right"><a class="locale-link" href="'''+prefix+t['switch']+'''">'''+('PL' if not pl else 'EN')+''' ↗</a><button class="nav-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="mobile-nav" aria-label="Menu"><span></span><span></span></button></div></div></header>
<div class="mobile-panel" id="mobile-nav" aria-hidden="true"><div class="container"><p class="eyebrow">MENU</p><nav aria-label="Mobile navigation">'''+navigation+'''</nav></div></div>
<main id="main">
<section class="p-hero"><div class="container p-hero__grid"><div><p class="eyebrow p-gold">'''+h(t['eyebrow'])+'''</p><h1>'''+h(d['name'])+'''</h1><p class="p-hero__subtitle">'''+h(d['subtitle'])+'''</p><p class="p-hero__intro">'''+h(d['intro'])+'''</p><div class="p-hero__actions"><a href="'''+prefix+t['publications']+'''">'''+h(d['ctaBooks'])+''' ↗</a><a href="#credentials">'''+h(t['background'])+''' ↓</a></div></div>
<div class="p-hero__photo"><img src="'''+prefix+'''assets/portraits/hero.webp" width="900" height="1120" alt="'''+h(d['name'],quote=True)+''' — portrait" fetchpriority="high"><span>DKK / QUEENSLAND · AUSTRALIA</span></div></div></section>
<section class="p-strip"><div class="container p-strip__inner"><span>'''+h(t['early'])+'''</span><span>'''+h(t['period'])+'''</span><span>PACFA / CLINICAL REGISTRANT</span></div></section>
<section class="p-section p-section--paper" id="background"><div class="container p-two"><div><p class="eyebrow p-caps">01 / '''+h(t['background'])+'''</p><h2>'''+h(t['story'])+'''</h2></div><div class="p-prose">'''+bio+'''</div></div></section>
<section class="p-section" id="credentials"><div class="container"><div class="p-heading"><p class="eyebrow p-caps">02 / '''+h(t['qualificationsTitle'] if 'qualificationsTitle' in t else d['qualificationsTitle'])+'''</p><h2>'''+h(d['qualificationsTitle'])+'''</h2></div><div class="p-card-grid">'''+block_list(d['qualifications'])+'''</div><div class="p-heading p-heading--second"><h2>'''+h(d['registrationsTitle'])+'''</h2></div><div class="p-card-grid">'''+block_list(d['registrations'])+'''</div><div class="p-heading p-heading--second"><h2>'''+h(d['additionalTitle'])+'''</h2></div><div class="p-card-grid">'''+block_list(d['additional'])+'''</div></div></section>
<section class="p-section p-section--paper"><div class="container p-two"><div><p class="eyebrow p-caps">03 / '''+h(t['practice'])+'''</p><h2>'''+h(d['practiceTitle'])+'''</h2><p class="p-intro">'''+h(d['practice'])+'''</p></div><div><h3 class="p-side-title">'''+h(d['scopeTitle'])+'''</h3><ul class="p-scope">'''+practice+'''</ul></div></div></section>
<section class="p-section"><div class="container"><div class="p-heading"><p class="eyebrow p-caps">04 / '''+h(t['role'])+'''</p><h2>'''+h(d['leadershipTitle'])+'''</h2><p>'''+h(d['leadershipText'])+'''</p></div><div class="p-roles">'''+roles+'''</div><a class="p-inline-link" href="'''+prefix+t['leadership']+'''">'''+h(d['ctaLeadership'])+''' ↗</a></div></section>
<section class="p-section p-section--deep"><div class="container p-two"><div><p class="eyebrow p-gold">05 / '''+h(t['publicationDate'])+'''</p><h2>'''+h(d['publicationsTitle'])+'''</h2><p>'''+h(d['publicationsText'])+'''</p><a class="p-inline-link" href="'''+prefix+t['publications']+'''">'''+h(d['ctaBooks'])+''' ↗</a></div>
<div><p class="eyebrow p-gold">'''+h(d['sourcesTitle'])+'''</p><div class="p-sources">'''+externals+'''</div></div></div></section>
<section class="p-section p-section--contact"><div class="container p-contact"><div><p class="eyebrow p-caps">06 / '''+h(d['contactTitle'])+'''</p><h2>'''+h(d['ctaContact'])+'''</h2><p>'''+h(d['contactText'])+'''</p></div><div class="p-contact__links"><a href="mailto:'''+h(SITE['email'])+'''">'''+h(SITE['email'])+''' ↗</a><a href="'''+prefix+t['media']+'''">'''+h(d['ctaMedia'])+''' ↗</a></div></div></section>
</main><footer class="footer"><div class="container"><div class="footer-top"><a class="footer-brand" href="'''+prefix+t['home']+'''">DKK.</a><nav class="footer-nav" aria-label="Footer navigation">'''+navigation+'''</nav></div><div class="footer-bottom"><span>© '''+h(d['name'])+''' · PROFESSIONAL PROFILE</span><a href="#top">↑ '''+('Back to top' if not pl else 'Do góry')+'''</a></div></div></footer></body></html>'''
    path=ROOT/t['profile']/'index.html'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(markup,'utf-8')

def add_proof_bar(src,lang,pre):
    d=PROFILE[lang];t=LANG[lang];pl=lang=='pl'
    bar='<section class="p-home-evidence" aria-label="'+('Professional credentials' if not pl else 'Podstawowe informacje zawodowe')+'"><div class="container p-home-evidence__inner"><span><strong>PACFA</strong> Clinical Registrant</span><span><strong>NDIS PBS</strong> '+('Assessed suitable' if not pl else 'Ocena suitable')+'</span><span><strong>2013—</strong> '+('Professional practice' if not pl else 'Praktyka zawodowa')+'</span><a href="'+pre+t['profile']+'">'+h(t['link'])+' ↗</a></div></section>'
    src,n=re.subn(r'(</section>)(?=\s*<section id="selected")',lambda m:m.group(1)+bar,src,count=1,flags=re.S)
    if n!=1:raise RuntimeError('Homepage hero boundary not found')
    about='<section id="about"'
    a=src.find(about);b=src.find('</section>',a)
    if a<0 or b<0:raise RuntimeError('Homepage biography missing')
    intro=src[a:b]
    intro=re.sub(r'<a class="text-link reveal" href="[^"]*">[^<]*<span class="arrow">↗</span></a>',
        '<a class="text-link reveal" href="'+pre+t['profile']+'">'+h(t['link'])+' <span class="arrow">↗</span></a>',intro,count=1)
    src=src[:a]+intro+src[b:]
    # Precise, concise hero description; the evidence bar supplies professional qualifications.
    target=re.search(r'(<div class="hero-intro reveal"><p>)(.*?)(</p>)',src,re.S)
    if target:
        text=('Mental health clinician, psychotherapist, author and organisational leader. Working across practice, education, publications and institutional development.' if not pl else 'Specjalista zdrowia psychicznego, psychoterapeuta, autor i lider organizacji. Łączę praktykę, edukację, publikacje i rozwój instytucji.')
        src=src[:target.start(2)]+h(text)+src[target.end(2):]
    # The main heading stays the person's name, but add an explicit professional description to assist scanning.
    return src

def update_catalogue(src,lang,pre):
    valid=[x for x in PUBLICATIONS if x.get('status')=='published']
    valid.sort(key=lambda x:x.get('date',''),reverse=True)
    tiles=[]
    for i,p in enumerate(valid):
        title=h(p.get('titleShort',p['title']).get(lang,p['title'][lang]))
        full=h(p['title'][lang])
        srcimg=h(pre+p['cover'],quote=True)
        path=pre+('works/' if lang=='en' else 'pl/publikacje/')+p['slug']+'/'
        kind={'article':('Article','Artykuł'),'research':('Research paper','Opracowanie badawcze'),'working_paper':('Working paper','Working paper'),'book':('Book','Książka')}.get(p['kind'],('Publication','Publikacja'))[lang=='pl']
        tiles.append('<a class="publication-tile" style="--tile-index:'+str(min(i,11))+'" href="'+h(path,quote=True)+'" aria-label="'+full+'"><div class="publication-tile__frame"><img src="'+srcimg+'" loading="lazy" decoding="async" width="660" height="880" alt="'+full+' — cover"><span class="publication-tile__arrow" aria-hidden="true">↗</span></div><div class="publication-tile__meta">'+h(kind)+' / '+h(p['year'])+'</div><h3>'+title+'</h3><p>'+h(p['subtitle'][lang])+'</p></a>')
    start=src.find('<div class="pub-grid" data-publications-grid>')
    end=src.find('</div><p class="pub-empty"',start)
    if start<0 or end<0:raise RuntimeError('Publication listing missing from '+lang)
    src=src[:start]+'<div class="pub-grid" data-publications-grid>'+''.join(tiles)+src[end:]
    src=re.sub(r'(<strong data-publication-count>)[^<]*(</strong>)',r'\g<1>'+str(len(valid)).zfill(2)+r'\g<2>',src)
    # Three featured covers are generated from the catalogue, not from static mockups.
    imgs=iter(valid[:3])
    def new_img(m):
        try:
            p=next(imgs)
        except StopIteration:
            return m.group()
        return '<img src="'+h(pre+p['cover'],quote=True)+'" width="660" height="880" alt="">'
    src=re.sub(r'<img src="[^"]+" width="660" height="880" alt="">',new_img,src,count=3)
    return src

def jsonld_for(path,lang):
    me=PROFILE[lang]['name'];selfurl=BASE+LANG[lang]['profile']
    person={"@type":"Person","@id":BASE+"#person","name":me,
            "alternateName":["Dawid Karol Kolodziej","Dawid Karol Kołodziej"],
            "url":BASE,"image":BASE+"assets/DawidKolodziej.png",
            "jobTitle":["Senior Mental Health Clinician","Psychotherapist","Counsellor","Organisational Leader"],
            "sameAs":[u for _,u in IDENTIFIERS],
            "description":PROFILE[lang]['intro']}
    if path.as_posix() in ('index.html','pl/index.html','profile/index.html','pl/profil/index.html'):
        return {"@context":"https://schema.org","@graph":[person,{"@type":"ProfilePage","@id":selfurl+"#webpage","url":selfurl,"mainEntity":{"@id":BASE+"#person"},"inLanguage":lang}]}
    if path.parts[0]=='works' or path.as_posix().startswith('pl/publikacje/') and len(path.parts)>3:
        slug=path.parts[-2]
        item=next((p for p in PUBLICATIONS if p['slug']==slug),None)
        if item is None or item.get('status')!='published':return None
        return {"@context":"https://schema.org","@type":"ScholarlyArticle" if item['kind']=='article' else "CreativeWork",
                "headline":item['title'][lang],"description":item['description'][lang],
                "author":{"@type":"Person","@id":BASE+"#person","name":me},
                "datePublished":item['date'],"inLanguage":lang,
                "image":BASE+item['cover'],
                "url":BASE+('works/' if lang=='en' else 'pl/publikacje/')+slug+'/',
                **({"identifier":"https://doi.org/"+item['doi']} if item.get('doi') else {})}
    return None

def repair_metadata(src,path,lang):
    name=PROFILE[lang]['name'];s=src
    if path.as_posix() in ('index.html','pl/index.html'):
        title=name+" — Mental Health, Research & Leadership" if lang=='en' else name+" — zdrowie psychiczne, publikacje i organizacje"
        s=re.sub(r'<title>.*?</title>','<title>'+h(title)+'</title>',s,count=1,flags=re.S)
        s=re.sub(r'<meta property="og:title" content="[^"]*">','<meta property="og:title" content="'+h(title,quote=True)+'">',s,count=1)
        s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+h(PROFILE[lang]['intro'],quote=True)+'">',s,count=1)
        s=re.sub(r'<meta property="og:description" content="[^"]*">','<meta property="og:description" content="'+h(PROFILE[lang]['intro'],quote=True)+'">',s,count=1)
    if path.as_posix() in ('publications/index.html','pl/publikacje/index.html'):
        first=next((p for p in PUBLICATIONS if p.get('status')=='published'),None)
        if first:
            s=re.sub(r'<meta property="og:image" content="[^"]*">','<meta property="og:image" content="'+BASE+h(first['cover'],quote=True)+'">',s,count=1)
        old_text=('Five links to Google Play Books. Covers and verified author-matched titles are fetched from Google\'s catalogue when available.' if lang=='en' else 'Pięć odnośników do katalogu Google Play Books. Tytuły i okładki są pobierane z oficjalnych metadanych, jeśli są dostępne.')
        new_text=('A selection of available digital editions. The growing catalogue above includes links to the relevant stores and source records.' if lang=='en' else 'Wybrane dostępne wydania cyfrowe. Rozwijający się katalog powyżej zawiera odnośniki do księgarni i źródeł.')
        s=s.replace(old_text,new_text)
    if path.parts[0]=='works' or (path.parts[0]=='pl' and len(path.parts)>3 and path.parts[1]=='publikacje'):
        slug=path.parts[-2]
        item=next((p for p in PUBLICATIONS if p['slug']==slug),None)
        if item:
            s=re.sub(r'<meta property="og:image" content="[^"]*">','<meta property="og:image" content="'+BASE+h(item['cover'],quote=True)+'">',s,count=1)
    ld=jsonld_for(path,lang)
    s=re.sub(r'<script type="application/ld\+json">[\s\S]*?</script>','',s)
    if ld:s=s.replace('</head>','<script type="application/ld+json">'+js(ld)+'</script></head>',1)
    if 'name="twitter:card"' not in s:s=s.replace('</head>','<meta name="twitter:card" content="summary_large_image"></head>',1)
    return s

def update():
    for lang in ('en','pl'):profile_page(lang)
    targets=[Path('index.html'),Path('pl/index.html'),Path('profile/index.html'),Path('pl/profil/index.html'),
             Path('publications/index.html'),Path('pl/publikacje/index.html')]
    targets += [p.relative_to(ROOT) for p in ROOT.glob('works/*/index.html')]
    targets += [p.relative_to(ROOT) for p in ROOT.glob('pl/publikacje/*/index.html')]
    targets += [p.relative_to(ROOT) for p in ROOT.glob('leadership/index.html')]
    targets += [p.relative_to(ROOT) for p in ROOT.glob('media/index.html')]
    targets += [p.relative_to(ROOT) for p in ROOT.glob('gallery/index.html')]
    targets += [p.relative_to(ROOT) for p in ROOT.glob('pl/organizacje/index.html')]
    targets += [p.relative_to(ROOT) for p in ROOT.glob('pl/media/index.html')]
    targets += [p.relative_to(ROOT) for p in ROOT.glob('pl/galeria/index.html')]
    for path in targets:
        lang='pl' if path.parts[0]=='pl' else 'en'
        pre=relative(path)
        source=(ROOT/path).read_text('utf-8')
        # Reuse current five navigation positions; no extra menu width.
        navigation=nav(pre,lang)
        for kind in ('nav-links','footer-nav'):
            source=re.sub(r'(<nav class="'+kind+r'"[^>]*>)[\s\S]*?(</nav>)',
                          lambda m:m.group(1)+navigation+m.group(2),source,count=1)
        source=re.sub(r'(<nav aria-label="Mobile navigation">)[\s\S]*?(</nav>)',
                      lambda m:m.group(1)+navigation+m.group(2),source,count=1)
        if path.as_posix() in ('index.html','pl/index.html'):
            source=add_proof_bar(source,lang,pre)
        if path.as_posix() in ('publications/index.html','pl/publikacje/index.html'):
            source=update_catalogue(source,lang,pre)
        if path.as_posix() in ('media/index.html','pl/media/index.html','leadership/index.html','pl/organizacje/index.html'):
            line=('Professional profile and collaboration' if lang=='en' else 'Profil zawodowy i współpraca')
            source=source.replace('</main>','<section class="p-mini-cta"><div class="container"><span>'+h(line)+'</span><a href="'+pre+LANG[lang]['profile']+'">'+h(LANG[lang]['link'])+' ↗</a><a href="mailto:'+h(SITE['email'])+'">'+h(PROFILE[lang]['ctaContact'])+' ↗</a></div></section></main>',1)
        source=repair_metadata(source,path,lang)
        (ROOT/path).write_text(source,'utf-8')
    print('Refreshed professional identity, publication archive and metadata in',len(targets),'bilingual pages.')

if __name__=='__main__':update()
