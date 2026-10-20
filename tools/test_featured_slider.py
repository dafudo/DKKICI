#!/usr/bin/env python3
"""Regression tests for the bilingual featured carousel: 0, 1, 2, 6, 7+ works."""
from pathlib import Path
from copy import deepcopy
import re
import tools.brand_refresh as brand

ROOT = Path(__file__).resolve().parents[1]
published = [p for p in brand.PUBLICATIONS if p.get('status') == 'published']
assert len(published) >= 7, "Need at least seven published test fixtures"

for lang, page, prefix in (
    ('en', 'publications/index.html', '../'),
    ('pl', 'pl/publikacje/index.html', '../../'),
):
    source = (ROOT / page).read_text(encoding='utf-8')
    for n in (0, 1, 2, 6, 7):
        old = brand.PUBLICATIONS
        try:
            new_data = deepcopy(old)
            active = 0
            for p in new_data:
                if p.get('status') == 'published':
                    p['spotlight'] = active < n
                    active += 1
            brand.PUBLICATIONS = new_data
            html = brand.update_catalogue(source, lang, prefix)
        finally:
            brand.PUBLICATIONS = old

        count = min(n, 6)
        assert len(re.findall(r'\sdata-featured-slide(?=\s|>)', html)) == count, (lang, n, 'slides')
        assert html.count('class="pub-highlight__item"') == count, (lang, n, 'cards')
        assert html.count('id="featured-publications"') == int(n > 0), (lang, n, 'visibility')
        assert html.count('data-featured-prev') == int(n > 1), (lang, n, 'prev')
        assert html.count('data-featured-next') == int(n > 1), (lang, n, 'next')
        assert html.count('data-featured-dot') == (count if n > 1 else 0), (lang, n, 'dots')
        assert html.count('data-featured-expand') == int(n > 6), (lang, n, 'expand')
        assert html.count('data-featured-dialog') == int(n > 6), (lang, n, 'modal')
        assert html.count('class="pub-featured-dialog__item"') == (n if n > 6 else 0), (lang, n, 'collection')
        if n:
            assert html.count('data-featured-slider') == 1, (lang, n, 'slider wrapper')
            assert html.count('data-featured-current') == int(n > 1), (lang, n, 'counter')
        if n > 1:
            assert html.count('hidden>') == count - 1, (lang, n, 'inactive cards hidden')
        assert html.count('<a class="publication-tile') == len(published), (lang, n, 'original catalogue unchanged')
    print(lang, 'featured carousel 0/1/2/6/7: OK')
