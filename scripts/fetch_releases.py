#!/usr/bin/env python3
"""
Récupère les nouvelles sorties (singles + albums) des 7 derniers jours
pour une liste d'artistes rap FR, classés par sous-catégorie.

Nécessite les variables d'environnement :
  SPOTIFY_CLIENT_ID
  SPOTIFY_CLIENT_SECRET

Usage:
  python fetch_releases.py
"""

import os
import sys
import json
import base64
import time
import datetime
import urllib.request
import urllib.parse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARTISTS_FILE = os.path.join(DATA_DIR, "artists.json")
RELEASES_FILE = os.path.join(DATA_DIR, "releases.json")

DAYS_WINDOW = int(os.environ.get("DAYS_WINDOW", "7"))


def get_token():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        sys.exit("Erreur: SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET doivent être définis.")

    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(),
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    return data["access_token"]


def api_get(url, token, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params, safe=",")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(e.headers.get("Retry-After", "2"))
                time.sleep(wait + 1)
                continue
            body = e.read().decode(errors="replace")
            print(f"    -> {e.code} {url} :: {body[:300]}", file=sys.stderr)
            raise
    raise RuntimeError("Trop de tentatives échouées")


def search_artist_id(name, token):
    data = api_get(
        "https://api.spotify.com/v1/search",
        token,
        {"q": f'artist:"{name}"', "type": "artist", "limit": 5, "market": "FR"},
    )
    items = data.get("artists", {}).get("items", [])
    if not items:
        return None
    # Privilégie le résultat dont le nom correspond exactement
    for item in items:
        if item["name"].lower() == name.lower():
            return item["id"], item["name"]
    return items[0]["id"], items[0]["name"]


def parse_release_date(album):
    date_str = album.get("release_date", "")
    precision = album.get("release_date_precision", "day")
    try:
        if precision == "day":
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        elif precision == "month":
            return datetime.datetime.strptime(date_str, "%Y-%m").date()
        else:
            return datetime.datetime.strptime(date_str, "%Y").date()
    except ValueError:
        return None


def get_recent_albums(artist_id, token, since_date):
    releases = []
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {
        "include_groups": "album,single",
        "market": "FR",
        "limit": 50,
    }
    while url:
        data = api_get(url, token, params)
        params = None  # next URL already has query params
        for album in data.get("items", []):
            rdate = parse_release_date(album)
            if rdate and rdate >= since_date:
                releases.append({
                    "title": album["name"],
                    "type": album["album_type"],
                    "release_date": album["release_date"],
                    "url": album["external_urls"]["spotify"],
                    "image": album["images"][0]["url"] if album.get("images") else None,
                })
        url = data.get("next")
    return releases


def main():
    with open(ARTISTS_FILE, "r", encoding="utf-8") as f:
        artists_by_category = json.load(f)

    token = get_token()
    today = datetime.date.today()
    since_date = today - datetime.timedelta(days=DAYS_WINDOW)

    all_releases = []
    seen = set()

    for category, names in artists_by_category.items():
        for name in names:
            try:
                result = search_artist_id(name, token)
            except Exception as e:
                print(f"[!] Erreur recherche '{name}': {e}", file=sys.stderr)
                continue
            if not result:
                print(f"[!] Artiste introuvable sur Spotify: {name}", file=sys.stderr)
                continue
            artist_id, real_name = result
            try:
                releases = get_recent_albums(artist_id, token, since_date)
            except Exception as e:
                print(f"[!] Erreur albums '{name}': {e}", file=sys.stderr)
                continue
            for r in releases:
                key = (real_name, r["title"], r["release_date"])
                if key in seen:
                    continue
                seen.add(key)
                r["artist"] = real_name
                r["category"] = category
                all_releases.append(r)
            time.sleep(0.1)

    # Tri par date de sortie décroissante
    all_releases.sort(key=lambda r: r["release_date"], reverse=True)

    output = {
        "generated_at": datetime.datetime.now().isoformat(),
        "since_date": since_date.isoformat(),
        "releases": all_releases,
    }

    with open(RELEASES_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=Fal