#!/usr/bin/env python3
"""Checks the pages build.py wrote, the way a search engine reads them. Run after build.py:
    python3 scripts/check_site.py
Every address of sitemap.xml must be a file whose canonical is that address, that names itself and
every other language of the page (hreflang, both ways, plus x-default), has one <h1>, a title and a
description of its own, the right lang and dir, and structured data that parses.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://luckgram.cc"
RTL = ("ar", "fa")
errors = []


def file_of(url):
    path = url[len(SITE):].lstrip("/")
    return os.path.join(ROOT, path, "index.html") if path.endswith("/") or not path else os.path.join(ROOT, path)


def read(url):
    try:
        with open(file_of(url), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
    urls = re.findall(r"<loc>([^<]+)</loc>", f.read())
if len(urls) != len(set(urls)):
    errors.append("sitemap.xml lists an address twice")

alternates, titles, descriptions = {}, {}, {}
for url in urls:
    html = read(url)
    if html is None:
        errors.append(f"{url}: in sitemap.xml, no file")
        continue
    bad = lambda what: errors.append(f"{url}: {what}")
    if re.findall(r'<link rel="canonical" href="([^"]+)">', html) != [url]:
        bad("canonical is not the page's own address")
    if 'name="robots" content="noindex"' in html:
        bad("noindex on a page of the sitemap")
    lang = re.search(r'<html lang="([^"]+)" dir="(ltr|rtl)">', html)
    if not lang:
        bad("no lang/dir on <html>")
        continue
    if (lang.group(2) == "rtl") != (lang.group(1).split("-")[0] in RTL):
        bad(f"dir={lang.group(2)} for lang={lang.group(1)}")
    alts = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', html))
    alternates[url] = alts
    if alts.get(lang.group(1)) != url:
        bad("does not name itself in hreflang")
    if "x-default" not in alts:
        bad("no hreflang x-default")
    if len(re.findall(r"<h1[ >]", html)) != 1:
        bad("not exactly one <h1>")
    title = re.search(r"<title>([^<]+)</title>", html)
    desc = re.search(r'<meta name="description" content="([^"]+)">', html)
    if not title or not desc:
        bad("no title or description")
    else:
        titles.setdefault(title.group(1), []).append(url)
        descriptions.setdefault(desc.group(1), []).append(url)
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(block)
        except ValueError as e:
            bad(f"structured data does not parse: {e}")
    if '<script type="application/ld+json">' not in html:
        bad("no structured data")
    for img in re.findall(r"<img [^>]*>", html):
        if " alt=" not in img or " width=" not in img:
            bad(f"image without alt or size: {img[:60]}")
    for href in set(re.findall(r'href="(/[^"#?]*)', html)):
        target = os.path.join(ROOT, href.lstrip("/"))
        if not os.path.exists(os.path.join(target, "index.html") if href.endswith("/") else target):
            bad(f"link to a page that does not exist: {href}")

for url, alts in alternates.items():
    for tag, other in alts.items():
        if tag == "x-default":
            continue
        if other not in alternates:
            errors.append(f"{url}: hreflang {tag} names {other}, which is not in sitemap.xml")
        elif url not in alternates[other].values():
            errors.append(f"{url}: hreflang {tag} is not answered by {other}")
for what, seen in (("title", titles), ("description", descriptions)):
    for text, where in seen.items():
        if len(where) > 1:
            errors.append(f"same {what} on {len(where)} pages: {text[:50]} ({', '.join(u[len(SITE):] for u in where[:4])})")

for name in ("robots.txt", "llms.txt", "llms-full.txt", "404.html", "assets/og.png"):
    if not os.path.exists(os.path.join(ROOT, name)):
        errors.append(f"{name} is missing")

for e in errors:
    print(e)
print(f"{len(urls)} pages checked, {len(errors)} problems")
sys.exit(1 if errors else 0)
