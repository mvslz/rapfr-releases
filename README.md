# Sorties Rap FR de la semaine

Site statique qui répertorie chaque semaine les nouvelles sorties (albums/singles)
d'artistes de rap français, classées en 3 catégories :

- 🔥 **Rap Mainstream**
- 🥂 **Rap Caviar**
- 💎 **Rap de Niche**

## Structure

```
rapfr-site/
├── data/
│   ├── artists.json     # Liste des artistes par catégorie (éditable)
│   └── releases.json    # Sorties détectées (généré automatiquement)
├── scripts/
│   ├── fetch_releases.py    # Interroge l'API Spotify
│   └── generate_site.py     # Génère index.html
├── index.html            # Le site (généré)
├── update.sh              # Lance fetch + generate (usage local)
└── .github/workflows/update.yml  # Automatisation hebdomadaire (GitHub Actions)
```

## Mise en place (GitHub Actions + GitHub Pages)

1. **Créer un dépôt GitHub** (public ou privé) et y pousser tout ce dossier.

2. **Ajouter les secrets Spotify** :
   - Sur GitHub : `Settings > Secrets and variables > Actions > New repository secret`
   - Ajouter `SPOTIFY_CLIENT_ID` et `SPOTIFY_CLIENT_SECRET`
     (obtenus sur https://developer.spotify.com/dashboard)

3. **Activer GitHub Pages** :
   - `Settings > Pages > Build and deployment > Source` → choisir **GitHub Actions**

4. **Lancer manuellement la première mise à jour** :
   - Onglet `Actions` > `Mise à jour hebdomadaire des sorties Rap FR` > `Run workflow`
   - Le site sera ensuite disponible à `https://<ton-pseudo>.github.io/<nom-du-repo>/`

5. Le workflow tourne ensuite automatiquement **chaque vendredi à 6h UTC**
   (modifiable dans `.github/workflows/update.yml`, ligne `cron`).

## Personnaliser les artistes

Édite `data/artists.json` pour ajouter/retirer des artistes dans chaque catégorie
(`caviar`, `mainstream`, `niche`). Les noms doivent correspondre (approximativement)
au nom exact de l'artiste sur Spotify.

## Fenêtre de temps

Par défaut, le script récupère les sorties des **7 derniers jours**.
Modifiable via la variable d'environnement `DAYS_WINDOW` dans le workflow.

## Test en local

```bash
export SPOTIFY_CLIENT_ID="..."
export SPOTIFY_CLIENT_SECRET="..."
cd rapfr-site
bash update.sh
# ouvrir index.html dans un navigateur
```
