#!/usr/bin/env python3
"""Localise only the personal surname in English static pages.

English pages use "Dawid Karol Kolodziej"; Polish pages keep "Dawid Karol Kołodziej".
Preserve source filenames, Polish-language titles and organisation names.
Runs after all generators so later rebuilds cannot reintroduce diacritics.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLACEMENTS = (
    ("KOŁODZIEJ", "KOLODZIEJ"),
    ("Kołodziej", "Kolodziej"),
    ("kołodziej", "kolodziej"),
)

def main() -> None:
    count = 0
    for page in ROOT.rglob("*.html"):
        rel = page.relative_to(ROOT)
        if "pl" in rel.parts or any(part.startswith(".") for part in rel.parts):
            continue
        original = page.read_text(encoding="utf-8")
        if 'lang="pl"' in original[:250] or "lang='pl'" in original[:250]:
            continue
        updated = original
        for before, after in REPLACEMENTS:
            updated = updated.replace(before, after)
        if original != updated:
            page.write_text(updated, encoding="utf-8")
            count += 1

    for page in ROOT.rglob("*.html"):
        rel = page.relative_to(ROOT)
        if "pl" in rel.parts:
            continue
        content = page.read_text(encoding="utf-8")
        for before, _ in REPLACEMENTS:
            assert before not in content, f"English surname was not localised in {rel}"
    print(f"English name normalisation verified; {count} page(s) changed.")

if __name__ == "__main__":
    main()
