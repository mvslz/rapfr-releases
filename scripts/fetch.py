#!/usr/bin/env python3
"""
Fetch recent Spotify releases for each artist in data/artists.json.
Writes data/releases.json.

Env vars required: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
Optional:         DAYS_WINDOW (default 7)
"""

import base64
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTISTS_FILE = os.path.join(ROOT, "data", "artists.json")
RELEASES_FILE = os.path.join(ROOT, "data", "releases.json")
DAYS_WINDOW = int(os.environ.get("DAYS_WINDOW", "7"))


def get_token():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID", "")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        sys.exit("ERREUR: SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET requis.")
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)["access_token"]


def api_get(url, token, params=None):
    if params:
        url = url + "?" + urllib.parse.urlencode(params, safe=",")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raw = int(e.headers.get("Retry-After", "2"))
                wait = min(raw, 30)  # jamais plus de 30s — au-delà on abandonne
                if raw > 30:
                    print(f"  rate-limit trop long ({raw}s), on passe.", flush=True)
                    return None
                print(f"  rate-limit, attente {wait}s...", flush=True)
                time.sleep(wait + 1)
                continue
            body = e.read().decode(errors="replace")
            print(f"  HTTP {e.code} -- {body[:200]}", file=sys.stderr)
            raise
    raise RuntimeError("Trop de tentatives echouees")


def find_artist(name, token):
    data = api_get(
        "https://api.spotify.com/v1/search",
        token,
        {"q": f'artist:"{name}"', "type": "artist", "limit": 5, "market": "FR"},
    )
    if data is None:
        return None
    items = data.get("artists", {}).get("items", [])
    if not items:
        return None
    for item in items:
        if item["name"].lower() == name.lower():
            return item["id"], item["name"]
    return items[0]["id"], items[0]["name"]


def parse_date(album):
    s = album.get("release_date", "")
    fmt = {"day": "%Y-%m-%d", "month": "%Y-%m", "year": "%Y"}.get(
        album.get("release_date_precision", "day"), "%Y-%m-%d"
    )
    try:
        return datetime.datetime.strptime(s, fmt).date()
    except ValueError:
        return None


def fetch_albums(artist_id, token, since):
    results = []
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {"include_groups": "album,single", "market": "FR", "limit": 50}
    while url:
        data = api_get(url, token, params)
        params = None
        if data is None:
            break
        for album in data.get("items", []):
            d = parse_date(album)
            if d and d >= since:
                results.append({
                    "title": album["name"],
                    "type": album["album_type"],
                    "release_date": album["release_date"],
                    "url": album["external_urls"].get("spotify", ""),
                    "image": album["images"][0]["url"] if album.get("images") else "",
                })
        url = data.get("next")
    return results


def main():
    with open(ARTISTS_FILE, encoding="utf-8") as f:
        artists_by_cat = json.load(f)

    token = get_token()
    today = datetime.date.today()
    since = today - datetime.timedelta(days=DAYS_WINDOW)
    print(f"Fenetre : {since} -> {today}", flush=True)

    releases = []
    seen = set()

    for category, names in artists_by_cat.items():
        for name in names:
            print(f"  {category} / {name}", flush=True)
            try:
                found = find_artist(name, token)
            except Exception as e:
                print(f"  [!] recherche echouee pour '{name}': {e}", file=sys.stderr)
                continue
            if not found:
                print(f"  [!] introuvable: {name}", file=sys.stderr)
                continue
            artist_id, real_name = found
            try:
                albums = fetch_albums(artist_id, token, since)
            except Exception as e:
                print(f"  [!] albums echoues pour '{name}': {e}", file=sys.stderr)
                continue
            for a in albums:
                key = (real_name, a["title"], a["release_date"])
                if key in seen:
                    continue
                seen.add(key)
                a["artist"] = real_name
                a["category"] = category
                releases.append(a)
            time.sleep(0.1)

    releases.sort(key=lambda r: r["release_date"], reverse=True)

    output = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "since_date": since.isoformat(),
        "releases": releases,
    }
    with open(RELEASES_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{len(releases)} sortie(s) trouvee(s) -> {RELEASES_FILE}", flush=True)


if __name__ == "__main__":
    main()
