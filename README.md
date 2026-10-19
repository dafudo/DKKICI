# DKK. — Personal Archive / osobista strona Dawida Karola Kołodzieja

## DKK brand, covers and online consultations (October 2026)

The canonical pages are `https://dkk.hqici.com/` and `https://dkk.hqici.com/pl/`. Professional enquiries use **dkk@hqici.com**. EN/PL copy refers to Australia-based psychotherapy practice with online consultations; this does not imply unrestricted provision across jurisdictions.

The site does **not** market itself as an "independent archive". Editorial presentation styling is maintained by `tools/finish_brand.py` and `css/brand-fixes.css`; the oversized chronology heading is no longer sticky, and the experience/credential bar has responsive spacing.

Favicon: `assets/favicon.svg` is the crisp DKK monogram. `tools/build_icons.py` generates `favicon-32x32.png`, `favicon-48x48.png` and `apple-touch-icon.png`. GitHub Actions commits these assets when the website is rebuilt.

### Publication cover authenticity

`data/publications.json` is authoritative for works and their preview artwork:

- `cover` is the local visual shown on this website.
- `coverSource: "editorial"` means the existing branded SVG is **not** presented as the official edition cover. The bilingual `coverNote` is displayed on the standalone work page.
- `retailerCover` retains an earlier source-matched Google Books thumbnail. Do not remove provenance when improving the visuals.
- `tools/improve_covers.py` attempts to find real, higher-quality, title-and-author-matched originals from confirmed Apple Books and Google Books item IDs. Unverified images and auto-generated white title pages are rejected. The separate workflow can also be run manually.
- When the author supplies the genuine publication artwork, upload the approved image to `assets/`, update `cover`, replace `coverSource` with an accurate source name, and remove `coverNote`. Never pretend website editorial artwork is a publisher cover.

The current digital-editions shelf shows **only confirmed Apple Books, Google Play Books and Amazon URLs** from each work's `links` array. New ICI blog or open-access publisher/aggregator URLs must be added to each corresponding publication record when verified; the website never invents them.

Full build sequence (after standard site generators):

```bash
python tools/build.py
python tools/showcase_pages.py
python tools/enrich_home.py
python tools/brand_refresh.py
python tools/localize_english_name.py
python tools/finish_brand.py
python tools/generate_sitemap.py
```

The canonical production workflow also installs Pillow and runs `tools/build_icons.py`.

---


## Current site — professional identity and publishing workflow (October 2026)

**Public domain:** https://dkk.hqici.com/

**Professional profile:** https://dkk.hqici.com/profile/ · https://dkk.hqici.com/pl/profil/

**Publications:** https://dkk.hqici.com/publications/ · https://dkk.hqici.com/pl/publikacje/

The active source for professional biographical facts, qualifications, PACFA registration, NDIS PBS suitable-practitioner wording, ongoing DBA studies and both languages is **`data/profile.json`**. Do not alter generated HTML to change these facts. The English public name is **Dawid Karol Kolodziej**; the Polish public name is **Dawid Karol Kołodziej**. Periods are intentionally distinguished: charity placements beginning in 2009 and professional counselling practice from 2013.

### Adding a new publication

1. Open `data/publications.json`, copy one complete entry, and replace the slug, bilingual titles/subtitles/descriptions, kind, subject, date, cover, and available source/store URLs.
2. Use `status: "published"` only for an actually released work, otherwise `status: "preview"`. Draft entries are excluded from the public index and sitemap.
3. Place a legally usable cover in `assets/`, use its repository-relative path as `cover`. Do not invent ISBNs, DOIs, peer review, or store availability.
4. Set `featured: true` for selected homepage works. The full library list, dynamic animated dialogs and Google Play editions are drawn from the **same** JSON file. Adding a new book does not require editing `index.html` or copying the store link into a second data file.
5. Commit on `main`. GitHub Actions regenerates both stand-alone detail pages, the static catalogue fallback, navigation metadata, `sitemap.xml`, `hreflang`, canonical URLs, and structured research metadata.

A `readUrl` should link to the full work or repository record. The `links` array can include Apple Books, Google Play Books and other *confirmed* edition URLs. Descriptive kinds currently supported: `article`, `research`, `working_paper`, `book`, `journal`, `resource`. Work descriptions must reflect the correct editorial/review status.

### Current build order

```bash
python3 tools/build.py
python3 tools/showcase_pages.py
python3 tools/enrich_home.py
python3 tools/brand_refresh.py
python3 tools/localize_english_name.py
python3 tools/generate_sitemap.py
```

The GitHub workflow `.github/workflows/build-site.yml` is the authoritative publishing process. Earlier instructions in this README describing a three-stage build, project-path URLs or removing `noindex` globally are historical and should not be followed for the current live site.

Professional certification, professional registration, assessed suitability, completed degrees, short courses and ongoing DBA studies are distinct categories. English and Polish descriptions should not suggest these are equivalent. Do not publish confidential case details or images as clinical testimonials.

---


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


## Canonical domain, sitemap and Google Search Console

**Canonical domain:** https://dkk.hqici.com/

**XML sitemap:** https://dkk.hqici.com/sitemap.xml

**Crawlers:** https://dkk.hqici.com/robots.txt

The repository-root `CNAME` file configures the GitHub Pages custom-domain name. For DNS, set a CNAME record with host `dkk` and target `dafudo.github.io` (never append `/DKKICI` to a DNS target). GitHub Pages Settings → Pages should display the matching custom domain and enable HTTPS once DNS has propagated. If the host points at a different platform, adjust the deployment provider instead of configuring two conflicting destinations.

The static build generates sitemap.xml and robots.txt, with canonicals and reciprocal English/Polish `hreflang` entries. Published works are indexed and previews are excluded. The gallery supplies image URLs. The generator runs whenever site content changes.

After the domain is accessible, verify the URL-prefix property `https://dkk.hqici.com/` in Google Search Console and submit `sitemap.xml` under **Indexing → Sitemaps**. Do not submit the old GitHub project URL; canonical links now point to the custom domain.

**Note:** DNS ownership is external to this repository. A committed CNAME file alone does not create the DNS record. Google indexing and rankings are not guaranteed.
