#!/bin/bash
# Met à jour les données et régénère le site.
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
set -a
source "$DIR/.env"
set +a
python3 "$DIR/scripts/fetch_releases.py"
python3 "$DIR/scripts/generate_site.py"
