# DKK. — Personal Archive / osobista strona Dawida Karola Kołodzieja

Dopasowywalne, dwujęzyczne portfolio redakcyjne w **czystym HTML + CSS + JavaScript**. Bez Astro, React, Next.js, `npm`, bazy danych i zewnętrznego CMS. Strona zawiera gotowe podstrony publikacji oraz prosty skrypt Pythona generujący kolejne strony z JSON-a.

**Status:** kompletny demonstrator wizualny i techniczny. **Przed promocją i indeksowaniem** zweryfikuj biografię, publikacje, rolę autora/redaktora, portrety, linki do książek i dane kontaktowe. W projekcie świadomie ustawiono `noindex,nofollow`, aby nie indeksować danych demonstracyjnych. Wszystkie przykładowe wpisy mają status `preview`.

## 1. Uruchomienie lokalne

Rozpakuj ZIP, otwórz terminal w katalogu projektu i uruchom:

```bash
python3 -m http.server 8000
```

Otwórz `http://localhost:8000` w przeglądarce. Strona otwiera się również z lokalnego pliku `index.html`, ale serwer HTTP lepiej symuluje GitHub Pages.

- Angielska wersja: `index.html` (strona główna).
- Polska wersja: `pl/index.html`.
- Strony publikacji po angielsku: `works/<slug>/index.html`.
- Strony publikacji po polsku: `pl/publikacje/<slug>/index.html`.

## 2. GitHub Pages: automatyczne wdrożenie (polecane)

1. Zaloguj się do GitHub i kliknij **New repository**.
2. Nadaj mu nazwę, np. `dawid-karol-kolodziej` lub `personal-archive`, ustaw **Public**, główną gałąź **main**.
3. Dodaj do katalogu głównego repozytorium **zawartość folderu projektu**, nie sam ZIP ani dodatkowy folder. Zachowaj również ukryte `.github/workflows/pages.yml` i `.nojekyll`.
4. Otwórz `Settings → Pages → Build and deployment → Source` i wybierz **GitHub Actions**.
5. Workflow `.github/workflows/pages.yml` uruchomi się przy zmianie gałęzi `main`, automatycznie wygeneruje HTML i wdroży stronę. W `Actions` sprawdzisz stan wdrożenia. W `Settings → Pages` zobaczysz faktyczny URL.

Dzięki tej metodzie przy kolejnych aktualizacjach wystarczy zmienić pliki w `data/` i zapisać commit na `main`; nie trzeba generować podstron na swoim komputerze. Źródło pozostaje na `main`, chociaż mechanizmem wdrożenia jest **GitHub Actions**, nie tryb „Deploy from a branch”.

### Alternatywa — dosłownie „Deploy from a branch: main / (root)”

Możesz też w `Settings → Pages` wybrać `Deploy from a branch`, `main`, `/(root)`. Wszystkie wstępne pliki HTML znajdują się już w paczce, więc strona zadziała. W tym wariancie po każdej zmianie `data/publications.json` lub `data/site.json` **uruchom lokalnie** `python3 tools/build.py` i wgraj również wygenerowane pliki HTML. Samo zmienienie JSON-a na GitHubie nie przebuduje katalogu statycznych podstron w trybie „Deploy from a branch”.

Adres standardowy projektu: `https://TWOJ-LOGIN.github.io/NAZWA-REPO/`. Własną domenę ustawisz później w `Settings → Pages → Custom domain`.

## 3. Dodawanie publikacji

Edytuj **`data/publications.json`**. Każda pozycja ma pola:

```json
{
  "slug": "nowa-publikacja",
  "title": {"pl":"Nowa publikacja", "en":"New publication"},
  "subtitle": {"pl":"Podtytuł", "en":"Subtitle"},
  "description": {"pl":"Krótki opis po polsku.", "en":"Brief English description."},
  "year": "2026",
  "date": "2026-10-18",
  "kind": "book",
  "category": "psychology",
  "featured": false,
  "status": "published",
  "cover": "assets/moja-okladka.webp",
  "links": [
    {"label":"Apple Books", "url":"https://books.apple.com/..."},
    {"label":"Google Play Books", "url":"https://play.google.com/store/books/..."}
  ],
  "readUrl": ""
}
```

Do `assets/` dodaj okładkę. Możesz używać `.jpg`, `.png`, `.webp`, `.svg`. Pole `slug` musi być unikalne i zawierać małe litery ASCII/cyfry/myślniki. Kategorie: `psychology`, `education`, `practice`, `ideas`. Typy: `book`, `journal`, `essay`, `resource`. Statusy: `preview`, `published`, `archived`. `featured: true` wyświetli pracę w sekcji wybranych publikacji, maksymalnie trzy pozycje; `published` usuwa ostrzeżenie na stronie konkretnej publikacji; `archived` ukrywa pozycję z katalogu.

Zaktualizuj stronę poleceniem:

```bash
python3 tools/build.py
```

**Uwaga:** przykładowe okładki SVG są fikcyjnymi projektami redakcyjnymi, a nie autentycznymi okładkami publikacji. Zastąp je własnymi materiałami. Dane przykładowe należy autoryzować.

## 4. Podmiana zdjęć, filmu i kontaktu

Otwórz `data/site.json`:

- `portrait`: wpisz np. `assets/portrait.webp` — Twoje zdjęcie w pierwszym ekranie. Domyślnie neutralny ilustracyjny placeholder SVG, nie zdjęcie innej osoby.
- `aboutPortrait`: wpisz np. `assets/desk-photo.webp` albo `assets/about-portrait.webp`. Puste pole oznacza zdjęcie stockowe Unsplash z graficznym fallbackiem.
- `videoUrl`: wpisz pełny URL filmu YouTube, np. `https://www.youtube.com/watch?v=VIDEO_ID`, albo bezpośredni adres HTTPS do `.mp4`/`.webm`. Puste pole otwiera gotowy panel koncepcyjny filmu.
- `email`: po wprowadzeniu adresu pojawi się aktywny przycisk kontaktowy `mailto:`.
- `linkedin`: pole przygotowane na przyszłe rozbudowanie kontaktu (obecny szablon go nie wyświetla).

Po zmianie danych uruchom `python3 tools/build.py` lub wypchnij commit na `main` z workflow GitHub Actions.

### Obrazy demonstracyjne i licencje

- Unsplash, **archiwum / półki z książkami**: https://unsplash.com/photos/a-row-of-bookshelves-in-a-library-at-night-7Evr-LSUSRY — użyte jako zewnętrzne zdjęcie w sekcji filmu.
- Unsplash, **biurko z książkami**: https://unsplash.com/photos/old-desk-with-books-inkwell-and-papers-znh0IwsP4kU — użyte w sekcji „About” jako zewnętrzne zdjęcie.
- Unsplash, **ciemna biblioteka**: https://unsplash.com/ja/%E5%86%99%E7%9C%9F/%E6%9C%AC%E3%81%8C%E4%B8%A6%E3%81%B6%E8%96%84%E6%9A%97%E3%81%84%E5%9B%B3%E6%9B%B8%E9%A4%A8-KFoFMYguEi4 — przygotowana do przyszłego użycia.
- Licencja Unsplash: https://unsplash.com/license — korzystanie z obrazów jest bezpłatne, również komercyjnie, z ograniczeniami licencji; podanie autora jest mile widziane.
- Pozostałe ilustracje SVG zostały przygotowane specjalnie do projektu jako materiały demonstracyjne.

Fotografie Unsplash są pobierane z `images.unsplash.com` w trakcie przeglądania witryny — **nie znajdują się fizycznie w ZIP**. Projekt działa również bez nich dzięki lokalnym placeholderom SVG / gradientom. Po zastąpieniu ich własnymi plikami w `assets/` wszystkie najważniejsze obrazy będą hostowane na GitHub Pages.

Nie wklejaj przypadkowego zdjęcia obcej osoby zamiast własnego portretu: mogłoby sugerować, że przedstawia właściciela strony.

## 5. Zmiana tekstów i animacji

- Teksty PL/EN, oś czasu i sekcje inicjatyw: `tools/build.py`, słownik `I`.
- Główne style: `css/style.css`.
- Animacje przewijania, wyszukiwarka, menu, film, kopiowanie linków: `js/main.js`.
- Publikacje i linki: `data/publications.json`.
- Osobiste dane/zdjęcia: `data/site.json`.

Animacje napisane są natywnie w CSS i JavaScript (IntersectionObserver); nie instalujesz żadnej biblioteki. Użytkownicy z włączonym `prefers-reduced-motion` otrzymują spokojniejszą wersję interfejsu.

## 6. Przed finalną publikacją

- Zweryfikuj biografię, role zawodowe, kwalifikacje, nazwy inicjatyw, dane publikacji.
- Wprowadź autentyczne fotografie oraz uzupełnij kontakt.
- Dodaj rzeczywiste linki do książek.
- Zastąp demonstracyjne okładki.
- Usuń `noindex,nofollow` z `tools/build.py` (znajdź `meta name="robots"`), uruchom generator i zatwierdź wygenerowane pliki.
- Ustaw canonical URL i adres domeny, gdy będziesz wiedzieć, gdzie strona faktycznie działa; następnie uzupełnij `og:image` do bezwzględnego URL.
- Sprawdź stronę z klawiatury oraz na telefonie i komputerze.

**Wszystkie pliki można wykorzystać i modyfikować w Twoim osobistym projekcie.**


## Bilingual publications catalogue (October 2026)

The dedicated editorial catalogues are served from:

- English: `/publications/`
- Polish: `/pl/publikacje/`

Clicking a publication cover opens an animated, keyboard-accessible native dialog with the title, cover, description, year, category, and available outbound reading or retailer links. The dialog also links to the existing static, shareable publication page. The catalogue includes search, subject filters, sorting, deep links using `?publication=<slug>`, mobile layout, and reduced-motion support.

**All publication data is read from `data/publications.json`.** Add verified links to each work, for example:

```json
"links": [
  {"label": "Apple Books", "url": "https://books.apple.com/..."},
  {"label": "Google Play Books", "url": "https://play.google.com/store/books/details/..."},
  {"label": "Amazon", "url": "https://www.amazon.com/..."},
  {"label": "Zanando", "url": "https://YOUR-VERIFIED-PUBLICATION-URL"}
]
```

Only valid HTTPS links supplied in the JSON file are displayed; do not use search or shop homepages as substitutes for verified book-specific URLs. The existing demo entries have empty `links` arrays.

The listing updates from JSON automatically. For a **new book**, also run `python3 tools/build.py` before committing so the separate English and Polish publication detail pages are generated. The generator preserves and links to both dedicated catalogues. No npm, build framework, or server database is necessary. Deploy files directly from the `main` branch root on GitHub Pages.

**Search indexing:** published works and the public biography may be indexed. Unverified draft publication pages remain `noindex,nofollow`; the public catalogue only displays published records.


## October 2026 — leadership, media and documentary portfolio

The site is now a bilingual personal portfolio rather than a generic psychotherapy landing page. There are six dedicated content pages:

- `/leadership/` and `/pl/organizacje/` — TPP President, PCA CEO and ICI Academic Director; organisation and business experience.
- `/media/` and `/pl/media/` — verified links to source broadcasters, interviews, professional speaking and community initiatives.
- `/gallery/` and `/pl/galeria/` — all 26 supplied `assets/photos` images, editorially described and optimised as WebP.

Data sources are `data/leadership.json`, `data/media.json`, `data/gallery.json` and `data/publications.json`. Image optimisation is handled by `tools/build_gallery.py`. The personal hero uses `assets/DawidKolodziej.png` with a compressed WebP source.

**To regenerate the full website:**

```bash
python3 tools/build.py
python3 tools/showcase_pages.py
python3 tools/enrich_home.py
```

The GitHub Actions workflow `.github/workflows/build-site.yml` runs these commands and publishes static HTML changes to `main` whenever the source data or generators change. The optional `.github/workflows/visual-qa.yml` performs responsive browser checks.

**Editorial standards:** 2009 denotes first charity placements; professional counselling practice dates from 2013. Current qualifications must not be retroactively attributed to earlier years. DBA is ongoing. Media reports involving sensitive family matters are linked in context, and known historical title misattributions are not reproduced as professional credentials. Two stylised compositions are labelled editorial, not event documentation. The MENTE mockup is retired. All 26 photographs supplied in `photos` are retained in the gallery; the older hand-picked portrait set was removed.


## Google Search Console — sitemap and search indexing

- **Live sitemap:** https://dafudo.github.io/DKKICI/sitemap.xml
- The file is committed to the `main` branch alongside `robots.txt`.
- **Submit in Search Console:** add and verify a URL-prefix property for
  `https://dafudo.github.io/DKKICI/`, go to **Indexing → Sitemaps**,
  and submit `sitemap.xml` (or its full URL).
- The sitemap includes the English and Polish versions of the homepage,
  publications index, media, gallery, leadership pages, and **published** book
  pages. Draft/preview records in `data/publications.json` are excluded.
- The sitemap includes `hreflang` alternates and gallery image URLs.
- `tools/generate_sitemap.py` also sets canonical and locale-alternate
  links in every public indexed HTML page. It is run at the end of
  `.github/workflows/build-site.yml`, after all HTML generators.
- **Important GitHub Pages limitation:** a `robots.txt` file under the
  repository-project path `/DKKICI/robots.txt` is **not** the host-root
  `https://dafudo.github.io/robots.txt`. Crawlers generally consult the
  host-root robots file; therefore you should submit the sitemap directly in
  Search Console, instead of relying on this project-level `robots.txt`.
- A submitted sitemap helps Google discover URLs; it does **not** guarantee
  indexing or a particular ranking.
