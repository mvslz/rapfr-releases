#!/usr/bin/env python3
"""Generate index.html from data/releases.json."""

import json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASES_FILE = os.path.join(ROOT, "data", "releases.json")
OUTPUT_FILE   = os.path.join(ROOT, "index.html")

SECTIONS = [
    ("caviar",     "01", "RAP CAVIAR",     "L'underground qui fait référence"),
    ("mainstream", "02", "MAINSTREAM",     "Ce que tout le monde écoute"),
    ("niche",      "03", "RAP DE NICHE",   "Pour ceux qui creusent"),
]

TYPE_LABELS = {"album": "ALBUM", "single": "SINGLE", "ep": "EP", "compilation": "COMPIL"}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:ital,wght@0,700;0,900;1,700&family=Barlow:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --red:    #ff2d2d;
  --black:  #080808;
  --card:   #111;
  --line:   #222;
  --white:  #f2f2f2;
  --muted:  #666;
  --font-display: 'Anton', sans-serif;
  --font-cond:    'Barlow Condensed', sans-serif;
  --font-body:    'Barlow', sans-serif;
}

html { scroll-behavior: smooth; }

body {
  background: var(--black);
  color: var(--white);
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.4;
  min-height: 100vh;
  overflow-x: hidden;
}

/* HEADER */
.site-header {
  border-bottom: 1px solid var(--line);
  overflow: hidden;
}

.header-top {
  display: flex;
  align-items: stretch;
  min-height: 180px;
}

.header-title {
  flex: 1;
  padding: 2rem 2.5rem;
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  position: relative;
}

.header-eyebrow {
  font-family: var(--font-cond);
  font-size: .7rem;
  font-weight: 700;
  letter-spacing: .3em;
  color: var(--red);
  text-transform: uppercase;
  position: absolute;
  top: 1.5rem;
  left: 2.5rem;
}

.header-title h1 {
  font-family: var(--font-display);
  font-size: clamp(3.5rem, 8vw, 7rem);
  line-height: .9;
  letter-spacing: -.01em;
  text-transform: uppercase;
}

.header-title h1 em {
  font-style: normal;
  color: var(--red);
  display: block;
}

.header-right {
  width: 260px;
  min-width: 200px;
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.header-count {
  font-family: var(--font-display);
  font-size: 4.5rem;
  line-height: 1;
}

.header-count-label {
  font-family: var(--font-cond);
  font-size: .75rem;
  font-weight: 700;
  letter-spacing: .15em;
  color: var(--muted);
  text-transform: uppercase;
  margin-top: .25rem;
}

.header-date {
  font-family: var(--font-cond);
  font-size: .75rem;
  font-weight: 700;
  letter-spacing: .1em;
  color: var(--muted);
  text-transform: uppercase;
  line-height: 1.8;
  border-top: 1px solid var(--line);
  padding-top: 1rem;
}

/* TICKER */
.ticker-wrap {
  overflow: hidden;
  border-top: 1px solid var(--line);
  background: var(--red);
  padding: .45rem 0;
}

.ticker {
  display: flex;
  white-space: nowrap;
  animation: ticker 30s linear infinite;
}

.ticker-item {
  font-family: var(--font-cond);
  font-size: .8rem;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--black);
  padding: 0 2rem;
}

@keyframes ticker {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}

/* NAV */
.site-nav {
  display: flex;
  border-bottom: 1px solid var(--line);
}

.site-nav a {
  display: flex;
  align-items: center;
  gap: .6rem;
  padding: 1rem 2rem;
  font-family: var(--font-cond);
  font-size: .85rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--muted);
  border-right: 1px solid var(--line);
  transition: color .15s, background .15s;
}

.site-nav a:hover { color: var(--white); background: #141414; }

.nav-num { font-size: .65rem; color: var(--red); }

/* SECTION */
.cat-section { border-bottom: 1px solid var(--line); }

.section-header {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid var(--line);
}

.section-num {
  width: 80px;
  min-width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 1.8rem;
  color: var(--red);
  border-right: 1px solid var(--line);
  padding: 1.2rem;
}

.section-info {
  padding: 1.2rem 2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: .25rem;
  border-right: 1px solid var(--line);
  flex: 1;
}

.section-name {
  font-family: var(--font-cond);
  font-size: clamp(1.6rem, 3vw, 2.4rem);
  font-weight: 900;
  letter-spacing: .04em;
  line-height: 1;
  text-transform: uppercase;
}

.section-tag {
  font-family: var(--font-cond);
  font-size: .7rem;
  font-weight: 700;
  letter-spacing: .2em;
  color: var(--muted);
  text-transform: uppercase;
}

.section-count {
  width: 80px;
  min-width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 1.4rem;
  color: var(--muted);
  padding: 1.2rem;
}

/* GRID */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1px;
  background: var(--line);
  border-top: 1px solid var(--line);
}

.empty-section {
  padding: 3rem 2rem;
  font-family: var(--font-cond);
  font-size: .85rem;
  letter-spacing: .1em;
  color: var(--muted);
  text-transform: uppercase;
}

/* CARD */
.card {
  background: var(--card);
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  transition: background .15s;
}

.card:hover { background: #181818; }

.card-img-wrap {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  background: #1a1a1a;
}

.card-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform .3s ease;
}

.card:hover .card-img-wrap img { transform: scale(1.04); }

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(8,8,8,.85) 0%, transparent 55%);
  opacity: 0;
  transition: opacity .2s;
  display: flex;
  align-items: flex-end;
  padding: .8rem;
}

.card:hover .card-overlay { opacity: 1; }

.card-play {
  width: 36px;
  height: 36px;
  border: 2px solid var(--white);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: .75rem;
  padding-left: 2px;
}

.card-placeholder {
  aspect-ratio: 1;
  background: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  opacity: .15;
}

.card-body {
  padding: .75rem .8rem .85rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-artist {
  font-family: var(--font-cond);
  font-size: .7rem;
  font-weight: 700;
  letter-spacing: .15em;
  text-transform: uppercase;
  color: var(--red);
  margin-bottom: .2rem;
}

.card-title {
  font-family: var(--font-cond);
  font-size: .95rem;
  font-weight: 900;
  line-height: 1.2;
  text-transform: uppercase;
  letter-spacing: .02em;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: .6rem;
  padding-top: .5rem;
  border-top: 1px solid var(--line);
}

.card-date {
  font-size: .65rem;
  letter-spacing: .05em;
  color: var(--muted);
}

.card-type {
  font-family: var(--font-cond);
  font-size: .6rem;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--black);
  background: var(--red);
  padding: .15rem .45rem;
  border-radius: 2px;
}

/* FOOTER */
.site-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2.5rem;
  border-top: 3px solid var(--red);
  font-family: var(--font-cond);
  font-size: .75rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--muted);
  flex-wrap: wrap;
  gap: 1rem;
}

.site-footer a { color: var(--muted); text-decoration: none; }
.site-footer a:hover { color: var(--white); }

.footer-logo {
  font-family: var(--font-display);
  font-size: 1.1rem;
  letter-spacing: .05em;
  color: var(--white);
}

.footer-logo span { color: var(--red); }

@media (max-width: 640px) {
  .header-right { display: none; }
  .header-title { border-right: none; }
  .site-nav a { padding: .8rem 1.2rem; font-size: .75rem; }
  .section-num, .section-count { width: 50px; min-width: 50px; font-size: 1.2rem; }
  .card-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
}
"""


def fmt_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").strftime("%d.%m.%Y")
    except Exception:
        return s


def card_html(r):
    label = TYPE_LABELS.get(r.get("type", "").lower(), r.get("type", "").upper())
    url   = r.get("url", "#")
    if r.get("image"):
        img = (
            '<div class="card-img-wrap">'
            f'<img src="{r["image"]}" alt="" loading="lazy">'
            '<div class="card-overlay"><div class="card-play">&#9654;</div></div>'
            '</div>'
        )
    else:
        img = '<div class="card-placeholder">&#127925;</div>'

    return (
        f'<a class="card" href="{url}" target="_blank" rel="noopener">'
        f'{img}'
        '<div class="card-body">'
        f'<div class="card-artist">{r["artist"]}</div>'
        f'<div class="card-title">{r["title"]}</div>'
        '<div class="card-meta">'
        f'<span class="card-date">{fmt_date(r["release_date"])}</span>'
        f'<span class="card-type">{label}</span>'
        '</div></div></a>'
    )


def section_html(key, num, label, tagline, by_cat):
    items = by_cat.get(key, [])
    count = len(items)
    if items:
        body = '<div class="card-grid">' + "".join(card_html(r) for r in items) + "</div>"
    else:
        body = '<div class="empty-section">Aucune sortie cette semaine.</div>'
    return (
        f'<section class="cat-section" id="{key}">'
        '<div class="section-header">'
        f'<div class="section-num">{num}</div>'
        '<div class="section-info">'
        f'<div class="section-name">{label}</div>'
        f'<div class="section-tag">{tagline}</div>'
        '</div>'
        f'<div class="section-count">{count}</div>'
        '</div>'
        f'{body}'
        '</section>'
    )


def make_ticker(releases):
    names = list(dict.fromkeys(r["artist"] for r in releases)) if releases else ["RAP", "FR", "SORTIES"]
    sep = ' &nbsp;&bull;&nbsp; '
    items = sep.join(n.upper() for n in names)
    full  = f'<span class="ticker-item">{items}</span>'
    return (
        '<div class="ticker-wrap">'
        f'<div class="ticker">{full}{full}{full}{full}</div>'
        '</div>'
    )


def main():
    try:
        with open(RELEASES_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    releases   = data.get("releases") or []
    since_date = data.get("since_date") or ""
    total      = len(releases)
    now_str    = datetime.datetime.utcnow().strftime("%d.%m.%Y")

    by_cat = {}
    for r in releases:
        by_cat.setdefault(r.get("category", ""), []).append(r)

    nav = "".join(
        f'<a href="#{key}"><span class="nav-num">{num}</span>&nbsp;{label}</a>'
        for key, num, label, _ in SECTIONS
    )

    sections = "".join(section_html(k, n, l, t, by_cat) for k, n, l, t in SECTIONS)
    ticker   = make_ticker(releases)

    since_fmt = ""
    if since_date:
        try:
            since_fmt = datetime.datetime.strptime(since_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        except Exception:
            since_fmt = since_date

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="fr">\n'
        '<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>Sorties Rap FR</title>\n'
        f'<style>{CSS}</style>\n'
        '</head>\n'
        '<body>\n'

        '<header class="site-header">\n'
        '<div class="header-top">\n'
        '<div class="header-title">\n'
        '<div class="header-eyebrow">Nouvelle semaine</div>\n'
        '<h1>Sorties<em>Rap FR</em></h1>\n'
        '</div>\n'
        '<div class="header-right">\n'
        '<div>\n'
        f'<div class="header-count">{total}</div>\n'
        '<div class="header-count-label">sorties cette semaine</div>\n'
        '</div>\n'
        '<div class="header-date">\n'
        f'Depuis le {since_fmt or "&mdash;"}<br>\n'
        f'Mis &agrave; jour le {now_str}\n'
        '</div>\n'
        '</div>\n'
        '</div>\n'
        f'{ticker}\n'
        '</header>\n'

        f'<nav class="site-nav">{nav}</nav>\n'

        f'<main>{sections}</main>\n'

        '<footer class="site-footer">\n'
        '<div class="footer-logo">Sorties <span>Rap FR</span></div>\n'
        '<div>'
        'Data &mdash; <a href="https://spotify.com" target="_blank">Spotify</a>'
        '&nbsp;&middot;&nbsp;'
        '<a href="https://github.com/mvslz/rapfr-releases" target="_blank">GitHub</a>'
        '</div>\n'
        '</footer>\n'

        '</body>\n</html>\n'
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html OK ({total} sortie(s))")


if __name__ == "__main__":
    main()
