#!/usr/bin/env python3
"""
Fetch recent Deezer releases for each artist in data/artists.json.
Writes data/releases.json.

No credentials required — Deezer public API.
Optional env var: DAYS_WINDOW (default 7)
"""

import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTISTS_FILE  = os.path.join(ROOT, "data", "artists.json")
RELEASES_FILE = os.path.join(ROOT, "data", "releases.json")
DAYS_WINDOW   = int(os.environ.get("DAYS_WINDOW", "7"))

BASE = "https://api.deezer.com"


def api_get(path, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.load(r)
            if isinstance(data, dict) and data.get("error"):
                err = data["error"]
                # quota exceeded — wait and retry
                if err.get("code") == 4:
                    wait = 5 * (attempt + 1)
                    print(f"  quota Deezer, attente {wait}s...", flush=True)
                    time.sleep(wait)
                    continue
                print(f"  erreur Deezer: {err}", file=sys.stderr)
                return None
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 10 * (attempt + 1)
                print(f"  rate-limit 429, attente {wait}s...", flush=True)
                time.sleep(wait)
                continue
            print(f"  HTTP {e.code} sur {url}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"  erreur reseau: {e}", file=sys.stderr)
            return None
    print(f"  trop de tentatives pour {url}", file=sys.stderr)
    return None


def find_artist(name):
    data = api_get("/search/artist", {"q": name, "limit": 10})
    if not data:
        return None
    items = data.get("data", [])
    if not items:
        return None
    # priorite a la correspondance exacte (insensible a la casse)
    for item in items:
        if item["name"].lower() == name.lower():
            return item["id"], item["name"]
    return items[0]["id"], items[0]["name"]


def fetch_albums(artist_id, since):
    results = []
    # Deezer limite a 25 par page — on pagine via le champ next
    path   = f"/artist/{artist_id}/albums"
    params = {"limit": 25, "index": 0}
    while path:
        data   = api_get(path, params)
        params = None  # l'URL next embarque deja les params
        if not data:
            break
        for album in data.get("data", []):
            raw_date = album.get("release_date", "")
            try:
                d = datetime.date.fromisoformat(raw_date)
            except ValueError:
                continue
            if d < since:
                continue
            record_type = album.get("record_type", "album").lower()
            if record_type == "compilation":
                continue
            cover = (
                album.get("cover_xl")
                or album.get("cover_big")
                or album.get("cover_medium")
                or album.get("cover")
                or ""
            )
            results.append({
                "title":        album["title"],
                "type":         record_type,
                "release_date": raw_date,
                "url":          album.get("link", ""),
                "image":        cover,
            })
        # next est une URL absolue ou absente
        next_url = data.get("next", "")
        if next_url:
            path   = next_url.replace("https://api.deezer.com", "")
            params = None
        else:
            path = None
    return results


def main():
    with open(ARTISTS_FILE, encoding="utf-8") as f:
        artists_by_cat = json.load(f)

    today = datetime.date.today()
    since = today - datetime.timedelta(days=DAYS_WINDOW)
    print(f"Fenetre : {since} -> {today}", flush=True)

    releases = []
    seen     = set()

    for category, names in artists_by_cat.items():
        for name in names:
            print(f"  {category} / {name}", flush=True)

            found = find_artist(name)
            if not found:
                print(f"  [!] introuvable: {name}", file=sys.stderr)
                time.sleep(0.3)
                continue

            artist_id, real_name = found
            albums = fetch_albums(artist_id, since)

            for a in albums:
                key = (real_name, a["title"], a["release_date"])
                if key in seen:
                    continue
                seen.add(key)
                a["artist"]   = real_name
                a["category"] = category
                releases.append(a)

            # petite pause pour rester dans les quotas Deezer (~50 req/5s)
            time.sleep(0.25)

    releases.sort(key=lambda r: r["release_date"], reverse=True)

    output = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "since_date":   since.isoformat(),
        "releases":     releases,
    }
    with open(RELEASES_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{len(releases)} sortie(s) trouvee(s) -> {RELEASES_FILE}", flush=True)


if __name__ == "__main__":
    main()
