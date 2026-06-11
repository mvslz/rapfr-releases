#!/usr/bin/env python3
"""
Génère le site statique (index.html) à partir de data/releases.json.
"""

import os
import json
import datetime
import html

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RELEASES_FILE = os.path.join(DATA_DIR, "releases.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "index.html")
CSS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")

CATEGORY_LABELS = {
    "caviar": "RAP CAVIAR",
    "mainstream": "MAINSTREAM",
    "niche": "DE NICHE",
}

CATEGORY_TAGLINES = {
    "caviar": "Le rap qui se déguste",
    "mainstream": "Ça tourne partout",
    "niche": "Pour les connaisseurs",
}

CATEGORY_ORDER = ["mainstream", "caviar", "niche"]

PLACEHOLDER_IMG = "https://placehold.co/400x400/111111/ff2d2d?text=%E2%99%AA&font=montserrat"


def card_html(release):
    title = html.escape(release["title"])
    artist = html.escape(release["artist"])
    rtype = release.get("type", "")
    date = release.get("release_date", "")
    url = release.get("url", "#")
    image = release.get("image") or PLACEHOLDER_IMG
    type_label = {"album": "Album", "single": "Single", "compilation": "Compilation"}.get(rtype, rtype)

    return f"""
        <a class="card" href="{html.escape(url)}" target="_blank" rel="noopener">
          <div class="cover" style="background-image:url('{html.escape(image)}')">
            <span class="card-type">{type_label}</span>
          </div>
          <div class="card-body">
            <div class="card-title">{title}</div>
            <div class="card-artist">{artist}</div>
            <div class="card-date">{date}</div>
          </div>
        </a>"""


def section_html(category, releases, index):
    label = CATEGORY_LABELS.get(category, category)
    tagline = CATEGORY_TAGLINES.get(category, "")
    num = f"{index:02d}"
    if not releases:
        body = '<p class="empty">Aucune nouvelle sortie cette semaine.</p>'
    else:
        body = '<div class="grid">' + "".join(card_html(r) for r in releases) + "</div>"
    return f"""
      <section class="category" id="{category}">
        <div class="cat-header">
          <span class="cat-num">{num}</span>
          <div>
            <h2>{label}</h2>
            <p class="cat-tagline">{tagline}</p>
          </div>
        </div>
        {body}
      </section>"""


def main():
    if os.path.exists(RELEASES_FILE):
        with open(RELEASES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"generated_at": None, "since_date": None, "releases": []}

    releases = data.get("releases", [])
    by_category = {c: [] for c in CATEGORY_ORDER}
    for r in releases:
        by_category.setdefault(r.get("category", "niche"), []).append(r)

    generated_at = data.get("generated_at")
    if generated_at:
        gen_dt = datetime.datetime.fromisoformat(generated_at)
        generated_str = gen_dt.strftime("%d/%m/%Y à %H:%M")
    else:
        generated_str = "jamais"

    since_date = data.get("since_date", "")

    sections = "".join(
        section_html(c, by_category.get(c, []), i + 1)
        for i, c in enumerate(CATEGORY_ORDER)
    )

    total = len(releases)

    html_doc = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SORTIES — Rap FR de la semaine</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo+Black&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <div class="header-inner">
      <span class="kicker">Mise à jour hebdo</span>
      <h1>SORTIES<br>RAP <span>FR</span></h1>
      <div class="meta-row">
        <span><strong>{total}</strong> sortie(s) depuis le {since_date}</span>
        <span>Dernière maj : <strong>{generated_str}</strong></span>
      </div>
    </div>
  </header>
  <main>
    {sections}
  </main>
  <footer>
    Généré automatiquement chaque semaine via l'API Spotify
  </footer>
</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_doc)

    print(f"Site généré : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
