#!/usr/bin/env python3
"""Generate index.html from data/releases.json."""

import json, os, datetime

ROOT          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASES_FILE = os.path.join(ROOT, "data", "releases.json")
OUTPUT_FILE   = os.path.join(ROOT, "index.html")

SECTIONS = [
    ("caviar",     "RAP CAVIAR",   "L'underground qui fait reference"),
    ("mainstream", "MAINSTREAM",   "Ce que tout le monde ecoute"),
    ("niche",      "RAP DE NICHE", "Pour ceux qui creusent"),
]

TYPE_LABELS = {"album": "ALBUM", "single": "SINGLE", "ep": "EP", "compilation": "COMPIL"}

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:ital,wght@0,600;0,700;0,900;1,700&family=Barlow:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --red:   #ff2d2d;
  --bk:    #080808;
  --c1:    #111;
  --ln:    #1e1e1e;
  --wh:    #f2f2f2;
  --mu:    #666;
  --fa:    'Anton', sans-serif;
  --fc:    'Barlow Condensed', sans-serif;
  --fb:    'Barlow', sans-serif;
}

html { scroll-behavior: smooth; }

body {
  background: var(--bk);
  color: var(--wh);
  font-family: var(--fb);
  font-size: 14px;
  line-height: 1.4;
  min-height: 100vh;
  overflow-x: hidden;
}

/* HEADER */
.site-header { border-bottom: 3px solid var(--red); }

.header-top { padding: 2rem 2.5rem 1.5rem; }

.site-header h1 {
  font-family: var(--fa);
  font-size: clamp(4rem, 10vw, 8rem);
  line-height: .88;
  letter-spacing: -.01em;
  text-transform: uppercase;
}

.site-header h1 em {
  font-style: normal;
  color: var(--red);
  display: block;
}

.header-sub {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1rem;
  flex-wrap: wrap;
  gap: .5rem;
}

.header-meta {
  font-family: var(--fc);
  font-size: .7rem;
  font-weight: 700;
  letter-spacing: .2em;
  color: var(--mu);
  text-transform: uppercase;
}

.header-count {
  font-family: var(--fa);
  font-size: 2rem;
  line-height: 1;
  display: flex;
  align-items: baseline;
  gap: .5rem;
}

.header-count span {
  font-family: var(--fc);
  font-size: .7rem;
  font-weight: 700;
  letter-spacing: .15em;
  color: var(--mu);
  text-transform: uppercase;
}

/* TICKER */
.ticker-wrap {
  overflow: hidden;
  background: var(--red);
  padding: .5rem 0;
}

.ticker {
  display: flex;
  white-space: nowrap;
  animation: tick 30s linear infinite;
}

.ticker-item {
  font-family: var(--fc);
  font-size: .8rem;
  font-weight: 700;
  letter-spacing: .15em;
  text-transform: uppercase;
  color: var(--bk);
  padding: 0 2rem;
}

@keyframes tick {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}

/* NAV */
.site-nav {
  display: flex;
  border-bottom: 1px solid var(--ln);
  overflow-x: auto;
}

.site-nav a {
  display: block;
  padding: .9rem 1.8rem;
  font-family: var(--fc);
  font-size: .8rem;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--mu);
  border-right: 1px solid var(--ln);
  white-space: nowrap;
  transition: color .15s, background .15s;
}

.site-nav a:hover { color: var(--wh); background: #141414; }

/* SECTION HEADER */
.cat-section { border-top: 1px solid var(--ln); }

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 1.2rem 2rem 0;
  gap: 1rem;
}

.section-name {
  font-family: var(--fa);
  font-size: clamp(2.5rem, 6vw, 5rem);
  text-transform: uppercase;
  line-height: .9;
  letter-spacing: .02em;
}

.section-tag {
  font-family: var(--fc);
  font-size: .7rem;
  font-weight: 700;
  letter-spacing: .18em;
  color: var(--mu);
  text-transform: uppercase;
  padding-bottom: .35rem;
  text-align: right;
}

/* GRID */
.card-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2px;
  background: var(--ln);
  margin-top: .75rem;
}

.empty-section {
  padding: 3rem 2rem;
  font-family: var(--fc);
  font-size: .85rem;
  letter-spacing: .1em;
  color: var(--mu);
  text-transform: uppercase;
}

/* CARD - image fills, text overlays bottom */
.card {
  background: #1a1a1a;
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  text-decoration: none;
  color: var(--wh);
  cursor: pointer;
  display: block;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform .35s ease;
}

.card:hover .card-img { transform: scale(1.06); }

.card-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3.5rem;
  color: #2a2a2a;
  background: #1a1a1a;
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,.92) 0%, rgba(0,0,0,.1) 55%, transparent 100%);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: .85rem .9rem .75rem;
  transition: background .2s;
}

.card:hover .card-overlay {
  background: linear-gradient(to top, rgba(0,0,0,.96) 0%, rgba(0,0,0,.25) 60%, transparent 100%);
}

.card-artist {
  font-family: var(--fc);
  font-size: .65rem;
  font-weight: 700;
  letter-spacing: .22em;
  text-transform: uppercase;
  color: var(--red);
  display: block;
  margin-bottom: .2rem;
}

.card-title {
  font-family: var(--fc);
  font-size: clamp(.85rem, 1.6vw, 1.05rem);
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: .03em;
  line-height: 1.1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-type {
  display: inline-block;
  font-family: var(--fc);
  font-size: .6rem;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--bk);
  background: var(--red);
  padding: .15rem .45rem;
  border-radius: 2px;
  margin-top: .5rem;
}

/* FOOTER */
.site-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2.5rem;
  border-top: 3px solid var(--red);
  margin-top: 2px;
  font-family: var(--fc);
  font-size: .75rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--mu);
  flex-wrap: wrap;
  gap: 1rem;
}

.site-footer a { color: var(--mu); text-decoration: none; }
.site-footer a:hover { color: var(--wh); }

.footer-logo {
  font-family: var(--fa);
  font-size: 1.1rem;
  letter-spacing: .05em;
  color: var(--wh);
}

.footer-logo span { color: var(--red); }

@media (max-width: 768px) {
  .card-grid { grid-template-columns: repeat(2, 1fr); }
  .header-top { padding: 1.5rem 1.5rem 1rem; }
  .section-head { padding: 1rem 1.5rem 0; }
}

@media (max-width: 480px) {
  .card-grid { grid-template-columns: repeat(2, 1fr); }
  .site-nav a { padding: .8rem 1.2rem; }
}
"""


def fmt_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").strftime("%d.%m.%Y")
    except Exception:
        return s


def card_html(r):
    label       = TYPE_LABELS.get(r.get("type", "").lower(), r.get("type", "").upper())
    spotify_url = r.get("url", "")
    url         = f"https://song.link/?url={spotify_url}" if spotify_url else "#"

    if r.get("image"):
        media = f'<img class="card-img" src="{r["image"]}" alt="" loading="lazy">'
    else:
        media = '<div class="card-placeholder">&#9836;</div>'

    return (
        f'<a class="card" href="{url}" target="_blank" rel="noopener">'
        f'{media}'
        '<div class="card-overlay">'
        f'<span class="card-artist">{r["artist"]}</span>'
        f'<div class="card-title">{r["title"]}</div>'
        f'<span class="card-type">{label}</span>'
        '</div>'
        '</a>'
    )


def section_html(key, label, tagline, by_cat):
    items = by_cat.get(key, [])
    if items:
        body = '<div class="card-grid">' + "".join(card_html(r) for r in items) + "</div>"
    else:
        body = '<div class="empty-section">Aucune sortie cette semaine.</div>'
    return (
        f'<section class="cat-section" id="{key}">'
        '<div class="section-head">'
        f'<div class="section-name">{label}</div>'
        f'<div class="section-tag">{tagline}</div>'
        '</div>'
        f'{body}'
        '</section>'
    )


def make_ticker(releases):
    names = list(dict.fromkeys(r["artist"] for r in releases)) if releases else ["RAP", "FR", "SORTIES"]
    sep   = ' &nbsp;&bull;&nbsp; '
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

    since_fmt = ""
    if since_date:
        try:
            since_fmt = datetime.datetime.strptime(since_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        except Exception:
            since_fmt = since_date

    nav = "".join(
        f'<a href="#{key}">{label}</a>'
        for key, label, _ in SECTIONS
    )

    sections = "".join(section_html(k, l, t, by_cat) for k, l, t in SECTIONS)
    ticker   = make_ticker(releases)

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
        '<h1>Sorties<em>Rap FR</em></h1>\n'
        '<div class="header-sub">\n'
        f'<div class="header-meta">Semaine du {since_fmt or now_str}&nbsp;&nbsp;&bull;&nbsp;&nbsp;Mis a jour {now_str}</div>\n'
        f'<div class="header-count">{total} <span>sorties</span></div>\n'
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
