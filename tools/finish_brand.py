#!/usr/bin/env python3
"""Final public-facing editorial polish for both site languages.

Run after the EN name localiser, before sitemap generation. Operates on the
generated HTML, so updates in build.py / showcase_pages.py remain compatible.
Do not replace genuine publication source URLs or alter work metadata.
"""
from pathlib import Path
from html import escape
import re
import hashlib

ROOT=Path(__file__).resolve().parents[1]

def translate_publications(page,lang):
    pl=lang=='pl'
    variants={
       'DKK / SELECTED COVERS':'',
       'DKK / SELECTED COVER':'',
       'DKK. / PUBLICATION ARCHIVE':'DKK. / PUBLIKACJE' if pl else 'DKK. / PUBLICATIONS',
       'THE COMPLETE ARCHIVE / INDEX 001':'PEŁNA LISTA PUBLIKACJI' if pl else 'ALL PUBLICATIONS',
       'A LIVING ARCHIVE / 2026':'PUBLIKACJE / 2026' if pl else 'PUBLICATIONS / 2026',
       'DIGITAL EDITIONS / GOOGLE PLAY':'WYBRANE WYDANIA CYFROWE' if pl else 'DIGITAL EDITIONS',
       'WYBRANE WYDANIA CYFROWE / GOOGLE PLAY':'WYBRANE WYDANIA CYFROWE',
       'Find me on<br><em>Google Play Books.</em>':'Digital<br><em>editions.</em>',
       'Dostępne w<br><em>Google Play Books.</em>':'Wydania<br><em>cyfrowe.</em>',
       "A selection of available digital editions. The growing catalogue above includes links to the relevant stores and source records.":"Books and other works are distributed through Apple Books, Google Play Books and Amazon as editions become available. Verified free-access records are linked on each publication page; additional ICI blog links will be added when confirmed.",
       "Wybrane dostępne wydania cyfrowe. Rozwijający się katalog powyżej zawiera odnośniki do księgarni i źródeł.":"Publikacje są stopniowo udostępniane w Apple Books, Google Play Books i Amazon. Zweryfikowane materiały w otwartym dostępie znajdziesz na stronach poszczególnych prac; odnośniki do bloga ICI zostaną uzupełnione po ich potwierdzeniu.",
       'AN INDEPENDENT COLLECTION · EST. 2025':'WRITING · RESEARCH · BOOKS',
       'NIEZALEŻNA KOLEKCJA · OD 2025':'ARTYKUŁY · BADANIA · KSIĄŻKI',
       'DKK. / INDEPENDENT ARCHIVE':'DKK. / PUBLICATIONS',
       'DKK. / NIEZALEŻNE ARCHIWUM':'DKK. / PUBLIKACJE',
       'An independent collection. New work is added as it is published.':'A growing collection of authored works, updated as new editions are released.',
       'Niezależna kolekcja. Nowe prace są dodawane wraz z ich publikacją.':'Rozwijający się dorobek autorski, uzupełniany wraz z publikacją kolejnych prac.',
       'DKK / INDEPENDENT ARCHIVE':'DKK / PUBLICATIONS',
    }
    for old,new in variants.items():
        page=page.replace(old,new)
    # Single set of author-library destinations, without repeating retailers under each work.
    if 'class="gp-section" id="bookstores"' in page:
        intro = ('Przeglądaj publikacje w bibliotekach autora i repozytorium Zenodo.' if pl else
                 'Explore published works in the author’s libraries and Zenodo repository.')
        title = 'Biblioteki cyfrowe' if pl else 'Digital editions'
        destinations = (
            ('Apple Books', 'https://books.apple.com/us/author/dawid-karol-ko%C5%82odziej/id1815567168'),
            ('Google Play Books', 'https://play.google.com/store/search?q=Dawid%20Karol%20Kolodziej&c=books'),
            ('Zenodo', 'https://zenodo.org/search?q=metadata.creators.person_or_org.name%3A%22Kolodziej%2C%20Dawid%20Karol%22&l=list&p=1&s=10&sort=bestmatch'),
        )
        from html import escape as esc
        links = ''.join(
            '<a href="'+esc(url, quote=True)+'" target="_blank" rel="noopener noreferrer">'+
            esc(label)+' ↗</a>' for label,url in destinations
        )
        replacement = ('<section class="gp-section" id="bookstores"><div class="container">'+
             '<div class="gp-section__top"><p class="eyebrow">'+esc(title)+'</p>'+
             '<h2>'+esc(title)+'</h2><p>'+esc(intro)+'</p></div>'+
             '<nav class="detail-actions" aria-label="'+esc(title)+'">'+links+'</nav>'+
             '</div></section>')
        page,count = re.subn(r'<section class="gp-section" id="bookstores">.*?</section>',
                    lambda _:replacement,page,count=1,flags=re.S)
        if count!=1:
            raise RuntimeError('Digital-editions shelf replacement failed')
    # Editorial cover-stack caption is redundant; remove instead of leaving empty decoration.
    page=re.sub(r'<span class="pub-stack__caption">\s*</span>','',page)
    return page

def revise_timeline(page,lang):
    note=re.search(r'<p class="dkk-timeline-note">([\s\S]*?)</p>',page)
    if not note:
        return page
    label=('2009 — pierwsze praktyki społeczne. Od 2013 — praktyka zawodowa w poradnictwie.'
           if lang=='pl' else
           '2009 — first charity placements. Professional counselling practice since 2013.')
    page=page[:note.start()]+page[note.end():]
    # Place the explanatory note in normal flow, above the actual chronology.
    page,count=re.subn(r'(<div class="journey-grid">[\s\S]*?</h2>\s*</div>)(<div class="timeline">)',
        lambda m: m.group(1)+m.group(2)+'<p class="dkk-timeline-context">'+escape(label)+'</p>',
        page,count=1)
    if count!=1: raise RuntimeError('Timeline insertion failed')
    return page

def main():
    pages=sorted(ROOT.glob('**/index.html'))
    for path in pages:
        # Skip non-public build helper folders if any are ever added.
        rel=path.relative_to(ROOT)
        lang='pl' if rel.parts[0]=='pl' else 'en'
        pl=lang=='pl'
        source=path.read_text('utf-8')
        source=source.replace('PERSONAL / ARCHIVE','PROFIL / DZIAŁALNOŚĆ' if pl else 'PROFESSIONAL / PROFILE')
        source=source.replace('PERSONAL ARCHIVE','PROFIL ZAWODOWY' if pl else 'PROFESSIONAL PROFILE')
        source=source.replace('INDEPENDENT DIGITAL ARCHIVE','PROFIL ZAWODOWY' if pl else 'PROFESSIONAL WEBSITE')
        source=source.replace('NIEZALEŻNE ARCHIWUM CYFROWE','PROFIL ZAWODOWY')
        source=source.replace('AN INDEPENDENT ARCHIVE','PROFESSIONAL WEBSITE')
        source=source.replace('DKK / PERSONAL ARCHIVE','DKK / PROFIL' if pl else 'DKK / PROFILE')
        source=source.replace('DKK / INDEPENDENT ARCHIVE','DKK / PROFIL' if pl else 'DKK / PROFILE')
        source=source.replace('DKK. / INDEPENDENT DIGITAL ARCHIVE','DKK. / PUBLICATIONS')
        source=source.replace('sdkk@psychopedagog.org','dkk@hqici.com')
        source=translate_publications(source,lang)
        if rel.as_posix() == 'pl/publikacje/index.html':
            source=source.replace('id="publication-dialog-title">Publication</h2>',
                                  'id="publication-dialog-title">Publikacja</h2>')
            source=source.replace('DKK. / PUBLICATIONS', 'DKK. / PUBLIKACJE')
        if rel.as_posix() in ('publications/index.html','pl/publikacje/index.html'):
            # Version the publication stylesheet to invalidate cached pre-spotlight CSS.
            css_file=ROOT/'css/publications.css'
            css_source=css_file.read_text('utf-8')
            css_version=hashlib.sha256(css_file.read_bytes()).hexdigest()[:12]
            source,ncss=re.subn(r'(href="[^"]*css/publications\.css)(?:\?[^"]*)?(")',
                lambda m:m.group(1)+'?v='+css_version+m.group(2),source,count=1)
            if ncss!=1:raise RuntimeError('Publication stylesheet not linked')
            # Critical component CSS is embedded, so a stale CDN asset can never
            # cause a cover to expand to its full natural dimensions again.
            start_marker='/* BEGIN DKK SPOTLIGHT COMPONENT */'
            end_marker='/* END DKK SPOTLIGHT COMPONENT */'
            # Remove stale critical rules even if there are no spotlight works.
            source,previous_critical=re.subn(
                r'<style id="dkk-spotlight-critical">[\s\S]*?</style>',
                '',source,flags=re.S
            )
            if previous_critical>1:
                raise RuntimeError('Duplicate critical spotlight style blocks')
            if 'id="featured-publications"' in source:
                if start_marker not in css_source or end_marker not in css_source:
                    raise RuntimeError('Spotlight CSS markers missing')
                critical=css_source.split(start_marker,1)[1].split(end_marker,1)[0].strip()
                source=source.replace('</head>','<style id="dkk-spotlight-critical">'+critical+'</style></head>',1)
            # Force refresh of the modal script after each JS change.
            version=hashlib.sha256((ROOT/'js/publications.js').read_bytes()).hexdigest()[:12]
            source=re.sub(r'(src="[^"]*js/publications\.js)(?:\?[^"]*)?(")',
                          lambda m:m.group(1)+'?v='+version+m.group(2), source)
        if rel.as_posix() in ('index.html','pl/index.html'):
            source=source.replace('QUEENSLAND · AUSTRALIA','POLSKA · AUSTRALIA' if pl else 'AUSTRALIA')
            source=source.replace('DKK / PROFESSIONAL WEBSITE','DKK / PROFIL' if pl else 'DKK / PROFILE')
            source=re.sub(r'<span class="eyebrow">(?:2009 EARLY CHARITY PLACEMENTS / PROFESSIONAL WORK FROM 2013|2009 PIERWSZE PRAKTYKI SPOŁECZNE / PRACA ZAWODOWA OD 2013)</span>',
                '<span class="eyebrow">'+('POLSKA · AUSTRALIA · KONSULTACJE ONLINE' if pl else 'AUSTRALIA · ONLINE CONSULTATIONS')+'</span>',source)
            source=revise_timeline(source,lang)
        if rel.as_posix() in ('profile/index.html','pl/profil/index.html'):
            source=source.replace('DKK / QUEENSLAND · AUSTRALIA','POLSKA · AUSTRALIA' if pl else 'AUSTRALIA')
        # Rely on assets committed in repository; do not link unknown external images.
        depth=len(rel.parts)-1
        pre='../'*depth
        if 'css/brand-fixes.css' not in source:
            source=source.replace('</head>','<link rel="stylesheet" href="'+pre+'css/brand-fixes.css"></head>',1)
        if 'apple-touch-icon' not in source:
            source=source.replace('</head>','<link rel="apple-touch-icon" sizes="180x180" href="'+pre+'assets/apple-touch-icon.png"><link rel="icon" type="image/png" sizes="32x32" href="'+pre+'assets/favicon-32x32.png"></head>',1)
        path.write_text(source,'utf-8')
    print('Finished',len(pages),'pages with corrected branding, biography and layout labels')

if __name__=='__main__':main()
