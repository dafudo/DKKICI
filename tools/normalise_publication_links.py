#!/usr/bin/env python3
"""Populate stable per-publication source buttons from canonical catalogue metadata.

Run before tools/build.py. Published pages always receive Zenodo, Apple Books,
and Google Play Books buttons. A verified edition link wins over an author
catalogue; a known Zenodo record wins over the creator's Zenodo archive.
The same publications.json powers static work pages and the JS catalogue modal.
New publications inherit buttons without three manual entries.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LABELS = ("Zenodo", "Apple Books", "Google Play Books")


def safe_url(url, hosts):
    if not isinstance(url, str) or not url.startswith("https://"):
        return ""
    parsed = urlsplit(url)
    return url if parsed.hostname in hosts and not parsed.username and not parsed.password else ""


def zenodo_record(url):
    url = safe_url(url, {"zenodo.org", "www.zenodo.org", "doi.org"})
    if not url:
        return ""
    p = urlsplit(url)
    if p.hostname in ("zenodo.org", "www.zenodo.org") and p.path.startswith("/records/"):
        identifier = p.path.removeprefix("/records/").strip("/")
        if identifier.isdigit():
            return "https://zenodo.org/records/" + identifier
    if p.hostname == "doi.org" and p.path.startswith("/10.5281/zenodo."):
        identifier = p.path.removeprefix("/10.5281/zenodo.")
        if identifier.isdigit():
            return "https://zenodo.org/records/" + identifier
    return ""


def edition_url(pub, label):
    allowed = {"Apple Books": {"books.apple.com"},
               "Google Play Books": {"play.google.com"}}[label]
    for item in pub.get("editionLinks", []):
        if item.get("label") == label:
            url = safe_url(item.get("url"), allowed)
            if url:
                return url
    if label == "Apple Books" and str(pub.get("appleBooksId", "")).isdigit():
        return "https://books.apple.com/us/book/id" + str(pub["appleBooksId"])
    if label == "Google Play Books" and pub.get("googlePlayId"):
        identifier = str(pub["googlePlayId"])
        if identifier.isalnum():
            return "https://play.google.com/store/books/details?id=" + identifier
    # Existing explicit individual-edition URLs may survive metadata migrations.
    for item in pub.get("links", []):
        if item.get("label") != label:
            continue
        url = safe_url(item.get("url"), allowed)
        if not url:
            continue
        if label == "Apple Books" and "/book/" in urlsplit(url).path:
            return url
        if label == "Google Play Books" and "/store/books/details" in urlsplit(url).path:
            return url
    return ""


def standard_links(pub, site):
    """Return exactly three standard links for published works, without fake edition claims."""
    if pub.get("status") != "published":
        return pub.get("links", [])

    zenodo = ""
    # A provided record is an explicit author instruction; do not infer a pending DOI.
    for candidate in (pub.get("zenodoUrl", ""), pub.get("readUrl", "")):
        zenodo = zenodo_record(candidate)
        if zenodo:
            break
    if not zenodo and pub.get("doi") and pub.get("doiStatus", "active") == "active":
        zenodo = zenodo_record("https://doi.org/" + pub["doi"])
    if not zenodo:
        for item in pub.get("links", []):
            if item.get("label") == "Zenodo":
                zenodo = zenodo_record(item.get("url"))
                if zenodo:
                    break

    archive = safe_url(site.get("zenodo", ""), {"zenodo.org", "www.zenodo.org"})
    apple_author = safe_url(site.get("appleBooksAuthor", ""), {"books.apple.com"})
    google_author = safe_url(site.get("googlePlayBooksAuthor", ""), {"play.google.com"})
    if not all((archive, apple_author, google_author)):
        raise ValueError("Missing or invalid author catalogue link in data/site.json")

    destinations = (
        ("Zenodo", zenodo or archive, "record" if zenodo else "author"),
        ("Apple Books", edition_url(pub, "Apple Books") or apple_author,
         "edition" if edition_url(pub, "Apple Books") else "author"),
        ("Google Play Books", edition_url(pub, "Google Play Books") or google_author,
         "edition" if edition_url(pub, "Google Play Books") else "author"),
    )
    links = [{"label": label, "url": url, "scope": scope}
             for label, url, scope in destinations]
    # Preserve other legitimate outbound links, without duplicating the standard buttons.
    for existing in pub.get("links", []):
        if existing.get("label") not in LABELS and str(existing.get("url", "")).startswith("https://"):
            links.append(existing)
    return links


def run():
    site = json.loads((ROOT / "data/site.json").read_text("utf-8"))
    data = ROOT / "data/publications.json"
    publications = json.loads(data.read_text("utf-8"))
    updated = 0
    for pub in publications:
        links = standard_links(pub, site)
        if links != pub.get("links", []):
            pub["links"] = links
            updated += 1
    if updated:
        data.write_text(json.dumps(publications, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    published = [p for p in publications if p["status"] == "published"]
    for p in published:
        assert [x["label"] for x in p["links"][:3]] == list(LABELS), p["slug"]
        assert len({x["label"] for x in p["links"][:3]}) == 3, p["slug"]
    print(f"Publication sources: {len(published)} published works, {updated} updated entries")


if __name__ == "__main__":
    run()
