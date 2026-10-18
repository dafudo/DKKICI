#!/usr/bin/env python3
"""Publish sitemap.xml and canonical/hreflang metadata for static GitHub Pages.

No dependencies. Only public, indexed pages are included; draft/preview
publications are excluded. Uses the custom subdomain https://dkk.hqici.com/ as canonical URL.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://dkk.hqici.com/"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NS = "http://www.w3.org/1999/xhtml"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"
ET.register_namespace("", SITEMAP_NS)
ET.register_namespace("xhtml", XHTML_NS)
ET.register_namespace("image", IMAGE_NS)

PUBLIC_SECTIONS = [
    ("", "pl/"),
    ("leadership/", "pl/organizacje/"),
    ("publications/", "pl/publikacje/"),
    ("media/", "pl/media/"),
    ("gallery/", "pl/galeria/"),
]

def url(route: str) -> str:
    return BASE + quote(route, safe="/-")

def route_file(route: str) -> Path:
    return ROOT / route / "index.html"

def is_indexable(page: Path) -> bool:
    if not page.is_file():
        raise FileNotFoundError(f"Missing public page: {page.relative_to(ROOT)}")
    contents = page.read_text(encoding="utf-8")
    if re.search(r'<meta\s+name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', contents, flags=re.I):
        return False
    return True

def pairs():
    result = list(PUBLIC_SECTIONS)
    publications = json.loads((ROOT / "data/publications.json").read_text("utf-8"))
    for work in publications:
        if work.get("status") != "published":
            continue
        slug = work["slug"]
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError(f"Unsafe publication slug: {slug}")
        result.append((f"works/{slug}/", f"pl/publikacje/{slug}/"))
    return result

def enrich_page(route: str, en_route: str, pl_route: str, lang: str) -> None:
    path = route_file(route)
    text = path.read_text(encoding="utf-8")
    # Remove former canonical/hreflang tags so rebuilds are idempotent.
    text = re.sub(r'<link\s+rel=["\']canonical["\'][^>]*>\s*', "", text, flags=re.I)
    text = re.sub(r'<link\s+rel=["\']alternate["\'][^>]*hreflang=[^>]*>\s*', "", text, flags=re.I)
    if "</head>" not in text:
        raise ValueError(f"Missing HTML head: {route}")
    current = url(route)
    meta = (
        f'<link rel="canonical" href="{current}">\n'
        f'<link rel="alternate" hreflang="en" href="{url(en_route)}">\n'
        f'<link rel="alternate" hreflang="pl" href="{url(pl_route)}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{url(en_route)}">\n'
    )
    text = text.replace("</head>", meta + "</head>", 1)
    path.write_text(text, encoding="utf-8")

def build() -> None:
    root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    gallery = json.loads((ROOT / "data/gallery.json").read_text("utf-8"))
    gallery_images = []
    for item in gallery:
        p = item["image"]
        if not p.startswith("assets/gallery/") or not (ROOT / p).is_file():
            raise FileNotFoundError(f"Gallery image missing: {p}")
        gallery_images.append(p)

    visited = set()
    count = 0
    for en, pl in pairs():
        if not is_indexable(route_file(en)) or not is_indexable(route_file(pl)):
            # Do not publish partly-indexable language pairs.
            continue
        for route, lang in ((en, "en"), (pl, "pl")):
            target = url(route)
            if target in visited:
                raise ValueError(f"Duplicate canonical URL: {target}")
            visited.add(target)
            enrich_page(route, en, pl, lang)
            item = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
            ET.SubElement(item, f"{{{SITEMAP_NS}}}loc").text = target
            for code, destination in (("en", en), ("pl", pl), ("x-default", en)):
                ET.SubElement(item, f"{{{XHTML_NS}}}link", {
                    "rel": "alternate",
                    "hreflang": code,
                    "href": url(destination),
                })
            if route in ("gallery/", "pl/galeria/"):
                for path in gallery_images:
                    image = ET.SubElement(item, f"{{{IMAGE_NS}}}image")
                    ET.SubElement(image, f"{{{IMAGE_NS}}}loc").text = url(path)
            elif route in ("", "pl/"):
                image = ET.SubElement(item, f"{{{IMAGE_NS}}}image")
                ET.SubElement(image, f"{{{IMAGE_NS}}}loc").text = url("assets/DawidKolodziej.png")
            count += 1

    ET.indent(root, space="  ")
    tree = ET.ElementTree(root)
    with (ROOT / "sitemap.xml").open("wb") as stream:
        tree.write(stream, encoding="utf-8", xml_declaration=True)

    # On the configured custom domain robots.txt is served at the host root.
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + BASE + "sitemap.xml\n",
        encoding="utf-8",
    )

    parsed = ET.parse(ROOT / "sitemap.xml")
    urls = parsed.findall(f"{{{SITEMAP_NS}}}url")
    if len(urls) != count or len(visited) != count:
        raise AssertionError("Sitemap URL counts differ")
    if any("fundamenty-motywacji" in x for x in visited):
        raise AssertionError("Preview work must not be indexed")
    print(f"Generated {count} indexable URLs with EN/PL alternates and {len(gallery_images)} gallery images.")

if __name__ == "__main__":
    build()
