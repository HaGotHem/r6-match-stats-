# Changelog - R6 Siege Match Stats Analyzer

## [Version 2.0] - Mise en forme Excel professionnelle

### ✨ Nouvelles fonctionnalités

#### 📂 Nommage automatique avec timestamp
- **Fichiers Excel datés** : Les rapports sont maintenant nommés avec la date et l'heure
  - Format : `Match_Stats_Complete_YYYY-MM-DD_HH-MM-SS.xlsx`
  - Exemple : `Match_Stats_Complete_2025-12-09_14-30-25.xlsx`
- **Historique préservé** : Gardez plusieurs analyses dans le même dossier
- **Pas d'écrasement** : Chaque nouvelle analyse crée un fichier unique
- **Script GUI adapté** : Détection automatique du dernier fichier généré

#### 🎨 Formatage Excel avancé
- **En-têtes colorés par catégorie** :
  - 🔴 Rouge (ATK) - Statistiques d'attaque
  - 🟢 Vert (DEF) - Statistiques de défense
  - 🟠 Orange (GLOBAL) - Statistiques globales
  - 🔵 Bleu marine - Colonnes générales (Joueur, Équipe)

- **Lignes alternées par équipe** :
  - 🔵 Bleu clair - Votre équipe
  - 🔴 Rouge clair - Équipe ennemie

- **Améliorations de lisibilité** :
  - ✅ Colonnes auto-ajustées selon le contenu
  - ✅ Bordures sur toutes les cellules
  - ✅ Noms de joueurs en gras
  - ✅ Première ligne figée (scroll sans perdre les en-têtes)
  - ✅ Alignement centré pour toutes les données
  - ✅ En-têtes avec hauteur augmentée (30px)

- **Timeline des kills** :
  - ✅ Headshots surlignés en jaune avec texte en gras
  - ✅ Formatage spécifique pour meilleure lecture

### 🐛 Corrections de bugs

#### Nettoyage automatique des données
- **Problème résolu** : Les analyses de matchs différents donnaient toujours les mêmes résultats
- **Solution** :
  - Nettoyage automatique des fichiers JSON avant chaque analyse
  - Renommage standardisé des fichiers (round01.json, round02.json, etc.)
  - Vérification du nombre de fichiers JSON avant analyse

#### Script GUI amélioré
- Ajout d'un compteur de fichiers .rec trouvés
- Ajout d'un compteur de fichiers JSON générés
- Messages plus clairs à chaque étape

### 🛠️ Nouveaux outils

- **clean.bat** : Script de nettoyage manuel des fichiers temporaires
- **test_formatting.py** : Script de test du formatage Excel

### 📝 Documentation

- README mis à jour avec :
  - Section dédiée à la mise en forme Excel
  - Instructions de nettoyage améliorées
  - Structure du projet actualisée
  - Avertissement sur le nettoyage automatique

---

## [Version 1.0] - Version initiale

### Fonctionnalités
- Parsing des fichiers .rec avec r6-dissect
- Analyse basique (analyze_match.py)
- Analyse complète ATK/DEF/GLOBAL (analyze_match_complete.py)
- Interface graphique (analyze_match_gui.bat)
- Statistiques avancées : KOST%, Survival Rate, Opening Kills/Deaths
- Timeline des kills
- Séparation par équipe
