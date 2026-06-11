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

CATEGORY_LABELS = {
    "caviar": "🥂 Rap Caviar",
    "mainstream": "🔥 Rap Mainstream",
    "niche": "💎 Rap de Niche",
}

CATEGORY_ORDER = ["mainstream", "caviar", "niche"]

PLACEHOLDER_IMG = "https://placehold.co/300x300/1a1a1a/ffffff?text=%E2%99%AA"


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
          <div class="cover" style="background-image:url('{html.escape(image)}')"></div>
          <div class="card-body">
            <div class="card-type">{type_label} · {date}</div>
            <div class="card-title">{title}</div>
            <div class="card-artist">{artist}</div>
          </div>
        </a>"""


def section_html(category, releases):
    label = CATEGORY_LABELS.get(category, category)
    if not releases:
        body = '<p class="empty">Aucune nouvelle sortie cette semaine.</p>'
    else:
        body = '<div class="grid">' + "".join(card_html(r) for r in releases) + "</div>"
    return f"""
      <section class="category" id="{category}">
        <h2>{label}</h2>
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

    sections = "".join(section_html(c, by_category.get(c, [])) for c in CATEGORY_ORDER)

    total = len(releases)

    html_doc = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sorties Rap FR de la semaine</title>
<style>
  :root {{
    --bg: #0d0d0f;
    --card-bg: #1a1a1e;
    --accent: #f5c518;
    --text: #f5f5f5;
    --muted: #9a9aa0;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
  }}
  header {{
    padding: 40px 24px 24px;
    text-align: center;
    border-bottom: 1px solid #2a2a2e;
  }}
  header h1 {{
    margin: 0 0 8px;
    font-size: 2rem;
    letter-spacing: -0.02em;
  }}
  header p {{
    margin: 4px 0;
    color: var(--muted);
    font-size: 0.9rem;
  }}
  main {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
  }}
  section.category {{
    margin-bottom: 48px;
  }}
  section.category h2 {{
    font-size: 1.4rem;
    margin-bottom: 16px;
    border-left: 4px solid var(--accent);
    padding-left: 12px;
  }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 16px;
  }}
  .card {{
    display: block;
    background: var(--card-bg);
    border-radius: 10px;
    overflow: hidden;
    text-decoration: none;
    color: var(--text);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }}
  .card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }}
  .cover {{
    width: 100%;
    aspect-ratio: 1 / 1;
    background-size: cover;
    background-position: center;
    background-color: #2a2a2e;
  }}
  .card-body {{
    padding: 10px 12px 14px;
  }}
  .card-type {{
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent);
    margin-bottom: 4px;
  }}
  .card-title {{
    font-weight: 600;
    font-size: 0.95rem;
    line-height: 1.3;
    margin-bottom: 2px;
  }}
  .card-artist {{
    font-size: 0.85rem;
    color: var(--muted);
  }}
  .empty {{
    color: var(--muted);
    font-style: italic;
  }}
  footer {{
    text-align: center;
    padding: 24px;
    color: var(--muted);
    font-size: 0.8rem;
    border-top: 1px solid #2a2a2e;
  }}
</style>
</head>
<body>
  <header>
    <h1>🎤 Sorties Rap FR de la semaine</h1>
    <p>{total} sortie(s) depuis le {since_date}</p>
    <p>Dernière mise à jour : {generated_str}</p>
  </header>
  <main>
    {sections}
  </main>
  <footer>
    Généré automatiquement chaque semaine via l'API Spotify.
  </footer>
</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_doc)

    print(f"Site généré : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
