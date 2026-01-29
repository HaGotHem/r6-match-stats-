# CURSOR.md

Ce fichier fournit le contexte du projet pour Cursor AI lors du travail sur ce dépôt.

## Vue d'ensemble du projet

R6 Siege Match Stats Analyzer - Application web Flask pour analyser les statistiques de matchs Rainbow Six Siege à partir de fichiers de replay (.rec) et générer des rapports Excel.

**Version:** 3.0.0  
**Plateforme:** Windows 10/11 (64-bit)  
**Langage:** Python 3.7+ avec backend Flask, frontend JavaScript vanilla

## Commandes

```bash
# Lancer depuis les sources
python main.py
# ou
python web/app.py

# Installer les dépendances
pip install -r requirements.txt

# Construire l'exécutable avec PyInstaller
python -m PyInstaller R6Analyst.spec

# Lancer via le batch (recommandé)
START_WEB_APP.bat
```

## Architecture

```
r6_analyst/
├── main.py                    # Point d'entrée PyInstaller, lance Flask + navigateur
├── START_WEB_APP.bat          # Lanceur Windows (détecte Python, installe deps)
├── R6Analyst.spec             # Configuration PyInstaller
├── requirements.txt           # Dépendances Python
├── web/
│   ├── app.py                 # Serveur Flask - toutes les routes API (~650 lignes)
│   └── templates/
│       └── index.html         # Interface single-page avec onglets (~1200 lignes)
├── src/
│   └── analyze_match_complete.py  # Moteur de stats - pandas/openpyxl (~490 lignes)
├── tools/
│   └── r6-dissect.exe         # Parser binaire pour fichiers .rec (outil externe v0.24.0)
└── data/                      # Données runtime (non versionnées)
    ├── uploads/               # Fichiers .rec uploadés
    ├── match_data/            # JSON temporaires de r6-dissect
    ├── reports/               # Rapports Excel générés
    └── config.json            # Configuration utilisateur (game_path, replay_path)
```

## Flux de données

1. **Utilisateur sélectionne des matchs** dans l'interface web
2. **Flask** appelle `r6-dissect.exe` pour parser les fichiers .rec → JSON
3. **analyze_match_complete.py** agrège les données JSON → pandas DataFrame
4. **openpyxl** formate et stylise → classeur Excel
5. **Utilisateur télécharge** le rapport

## Endpoints API principaux

| Route | But |
|-------|-----|
| `GET /api/config` | Charger la configuration utilisateur |
| `POST /api/config` | Sauvegarder le chemin du jeu |
| `GET /api/detect-game` | Auto-détecter l'installation R6 |
| `GET /api/replays` | Scanner le dossier MatchReplay |
| `POST /api/analyze` | Analyser les matchs sélectionnés |
| `POST /upload` | Upload de fichiers .rec (legacy) |
| `POST /analyze` | Analyser les fichiers uploadés (legacy) |
| `GET /download/<filename>` | Télécharger le rapport Excel |
| `GET /reports` | Lister tous les rapports disponibles |
| `GET /api/stats-options` | Obtenir les options de stats disponibles |

## Catégories de statistiques

9 catégories de stats configurables dans l'UI :
- **kills** : Kills / Deaths / K/D, KPR, +/-
- **kost** : KOST % (Kill, Objective, Survived, or Traded)
- **survival** : Rounds survécus, temps de survie total et moyen
- **headshots** : Headshots et HS%
- **opening** : Opening Kills/Deaths et ratio
- **multikills** : Multi-kills (2+ kills en 10 secondes)
- **plants** : Plantes et diffuses
- **teamkills** : Teamkills (désactivé par défaut)
- **rating** : Rating calculé (KPR + survival rate)

Chaque stat est calculée pour les 3 sides : **ATK** / **DEF** / **GLOBAL**

## Conventions de code

- Commentaires et noms de variables en français
- Sortie debug préfixée avec `[DEBUG]`, `[ERROR]`, `[OK]`, `[WARNING]`
- Configuration persistée dans `data/config.json`
- r6-dissect.exe est une dépendance binaire externe - ne pas modifier
- Gestion des chemins Windows avec détection automatique (Ubisoft Connect, Steam, Epic Games)
- Support PyInstaller avec gestion des chemins bundle/exe

## Détails techniques

### Analyse des matchs
- Support jusqu'à 20 rounds (overtime inclus)
- Parsing JSON avec validation de structure
- Détection automatique du rôle ATK/DEF par round
- Calcul KOST simplifié (Kill ou Survived)
- Multi-kills détectés si 2+ kills dans une fenêtre de 10 secondes

### Génération Excel
- Formatage professionnel avec couleurs par équipe
- En-têtes colorés par side (ATK=rouge, DEF=vert, GLOBAL=jaune)
- Colonnes auto-ajustées
- En-têtes figés (freeze panes)
- Plusieurs feuilles : Stats complètes, VOTRE EQUIPE, EQUIPE ENNEMIE

### Interface web
- Single-page application avec onglets
- Auto-détection des replays depuis MatchReplay
- Upload manuel avec drag & drop
- Filtres par type de match (Ranked/Scrim/Custom)
- Sélection personnalisée des statistiques
- Barre de progression simulée

## Limitations connues

- r6-dissect v0.24.0 peut ne pas reconnaître tous les opérateurs de Y10S4_01+
- Windows uniquement (chemins hardcodés)
- Port 5000 doit être disponible
- Taille maximale de fichier : 500MB
- Les fichiers .rec doivent être au format Dissect d'Ubisoft

## Notes importantes

- Le projet peut être compilé en exécutable standalone avec PyInstaller
- Les dossiers `data/` sont créés automatiquement au démarrage
- La configuration est sauvegardée après la première détection du jeu
- Les rapports sont nommés : `Map_DateGame_Type_DateAnalyse.xlsx`
- Les fichiers temporaires JSON sont nettoyés avant chaque analyse
