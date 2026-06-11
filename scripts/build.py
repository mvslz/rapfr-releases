#!/usr/bin/env python3
"""Generate index.html from data/releases.json. All styles are embedded."""

import json
import os
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASES_FILE = os.path.join(ROOT, "data", "releases.json")
OUTPUT_FILE = os.path.join(ROOT, "index.html")

SECTIONS = [
    ("caviar",     "RAP CAVIAR",     "L'underground qui fait reference"),
    ("mainstream", "RAP MAINSTREAM", "Ce que tout le monde ecoute"),
    ("niche",      "RAP DE NICHE",   "Pour ceux qui creusent"),
]

TYPE_LABELS = {"album": "ALBUM", "single": "SINGLE", "ep": "EP"}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Archivo+Black&family=Archivo:wght@400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--red:#ff2d2d;--bg:#0a0a0a;--card:#141414;--border:#222;--text:#f0f0f0;--muted:#888}
body{background:var(--bg);color:var(--text);font-family:'Archivo',sans-serif;min-height:100vh}
header{border-bottom:3px solid var(--red);padding:2rem 2rem 1.5rem;display:flex;align-items:flex-end;justify-content:space-between;gap:1rem;flex-wrap:wrap}
header h1{font-family:'Anton',sans-serif;font-size:clamp(2rem,5vw,3.5rem);letter-spacing:.03em;line-height:1;text-transform:uppercase}
header h1 span{color:var(--red)}
.header-meta{text-align:right;font-size:.8rem;color:var(--muted);line-height:1.6}
.header-meta strong{display:block;font-family:'Archivo Black',sans-serif;font-size:1.4rem;color:var(--text)}
section{padding:2.5rem 2rem;border-bottom:1px solid var(--border)}
section:last-child{border-bottom:none}
.section-header{display:flex;align-items:baseline;gap:1rem;margin-bottom:1.5rem}
.section-header h2{font-family:'Anton',sans-serif;font-size:clamp(1.4rem,3vw,2rem);letter-spacing:.05em}
.section-header h2::before{content:'';display:inline-block;width:6px;height:1em;background:var(--red);margin-right:.5rem;vertical-align:middle}
.section-tagline{font-size:.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:.1em}
.empty{color:var(--muted);font-style:italic;padding:1rem 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:1rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:4px;overflow:hidden;text-decoration:none;color:inherit;display:flex;flex-direction:column;transition:border-color .15s,transform .15s}
.card:hover{border-color:var(--red);transform:translateY(-2px)}
.card-cover{width:100%;aspect-ratio:1;object-fit:cover;background:#1a1a1a;display:block}
.card-placeholder{width:100%;aspect-ratio:1;background:#1a1a1a;display:flex;align-items:center;justify-content:center;font-size:2rem}
.card-body{padding:.6rem .7rem .8rem;flex:1;display:flex;flex-direction:column;gap:.25rem}
.card-title{font-family:'Archivo Black',sans-serif;font-size:.82rem;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card-artist{font-size:.75rem;color:var(--muted)}
.card-footer{display:flex;align-items:center;justify-content:space-between;margin-top:auto;padding-top:.4rem}
.card-date{font-size:.7rem;color:var(--muted)}
.card-type{font-size:.6rem;font-family:'Archivo Black',sans-serif;letter-spacing:.08em;padding:.15rem .4rem;border:1px solid var(--red);color:var(--red);border-radius:2px}
footer{text-align:center;padding:1.5rem;font-size:.75rem;color:var(--muted)}
footer a{color:var(--muted)}
"""


def card_html(r):
    cover = (
        f'<img class="card-cover" src="{r["image"]}" alt="" loading="lazy">'
        if r.get("image")
        else '<div class="card-placeholder">&#127925;</div>'
    )
    label = TYPE_LABELS.get(r.get("type", "").lower(), r.get("type", "").upper())
    url = r.get("url", "#")
    return (
        f'<a class="card" href="{url}" target="_blank" rel="noopener">'
        f"{cover}"
        f'<div class="card-body">'
        f'<div class="card-title">{r["title"]}</div>'
        f'<div class="card-artist">{r["artist"]}</div>'
        f'<div class="card-footer">'
        f'<span class="card-date">{r["release_date"]}</span>'
        f'<span class="card-type">{label}</span>'
        f"</div></div></a>"
    )


def section_html(key, label, tagline, by_cat):
    items = by_cat.get(key, [])
    body = (
        '<div class="grid">' + "".join(card_html(r) for r in items) + "</div>"
        if items
        else '<p class="empty">Aucune sortie cette semaine.</p>'
    )
    return (
        f'<section id="{key}">'
        f'<div class="section-header"><h2>{label}</h2>'
        f'<span class="section-tagline">{tagline}</span></div>'
        f"{body}</section>"
    )


def main():
    try:
        with open(RELEASES_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    releases = data.get("releases") or []
    since_date = data.get("since_date") or ""
    now_str = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
    total = len(releases)

    by_cat = {}
    for r in releases:
        by_cat.setdefault(r.get("category", ""), []).append(r)

    sections = "".join(section_html(k, l, t, by_cat) for k, l, t in SECTIONS)

    html = (
        "<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f"<title>Sorties Rap FR &mdash; semaine du {since_date or '...'}</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n"
        "<header>"
        "<h1>Sorties<br><span>Rap FR</span></h1>"
        '<div class="header-meta">'
        f"<strong>{total}</strong> sortie{'s' if total != 1 else ''} cette semaine"
        f"<br>depuis le {since_date or '...'}"
        f"<br>mis &agrave; jour {now_str}"
        "</div></header>\n"
        f"{sections}\n"
        "<footer>"
        'Donn&eacute;es <a href="https://spotify.com" target="_blank">Spotify</a>'
        " &mdash; "
        '<a href="https://github.com/mvslz/rapfr-releases" target="_blank">Code source</a>'
        "</footer>\n</body>\n</html>\n"
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html OK ({total} sortie(s))")


if __name__ == "__main__":
    main()
