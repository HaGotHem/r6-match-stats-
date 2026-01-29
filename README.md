# 🎮 R6 Siege Match Stats Analyzer - Interface Web

> Analyseur avancé de statistiques pour Rainbow Six Siege avec interface web moderne et drag & drop

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![Flask](https://img.shields.io/badge/flask-3.0+-red)

## ✨ Nouveautés Version 3.0

- 🌐 **Interface Web Moderne** : Glissez-déposez vos fichiers .rec directement dans le navigateur
- 📊 **Analyse en Temps Réel** : Suivez la progression de l'analyse
- 📁 **Gestion des Rapports** : Consultez et téléchargez tous vos rapports depuis l'interface
- 🎨 **Design Moderne** : Interface élégante et intuitive
- 📂 **Organisation Améliorée** : Structure de projet claire et professionnelle

## 🚀 Démarrage Rapide

### 1. Installation

```bash
# Cloner le projet
git clone https://github.com/VOTRE_USERNAME/r6-match-stats.git
cd r6-match-stats

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Lancement

**Double-cliquez sur `START_WEB_APP.bat`**

L'interface web s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:5000`

### 3. Utilisation

1. **Glissez-déposez** vos fichiers `.rec` dans la zone prévue
2. **Cliquez sur "Analyser le match"**
3. **Téléchargez** votre rapport Excel depuis l'onglet "Rapports générés"

C'est tout ! 🎉

## 📊 Statistiques Extraites

### Globales
- **Kills / Deaths / Assists**
- **K/D Ratio & +/-**
- **Headshots & Headshot %**

### Avancées
- **KPR** (Kills Per Round)
- **DPR** (Deaths Per Round)
- **Opening Kills/Deaths**
- **Survival Rate %**
- **KOST %** (Kill, Objective, Survived, or Traded)
- **Temps de Survie** (total et moyen)

### Rapports
- **Statistiques ATK/DEF/GLOBAL** séparées
- **Timeline complète** des kills avec headshots surlignés
- **Mise en forme professionnelle** avec couleurs par équipe
- **Export Excel** avec plusieurs feuilles

## 📁 Structure du Projet

```
r6-match-stats/
├── START_WEB_APP.bat          # 🚀 LANCEUR PRINCIPAL
├── requirements.txt            # Dépendances Python
│
├── src/                        # Scripts d'analyse Python
│   ├── analyze_match.py
│   ├── analyze_match_complete.py
│   └── test_formatting.py
│
├── web/                        # Interface web Flask
│   ├── app.py                 # Serveur backend
│   ├── templates/
│   │   └── index.html         # Interface drag & drop
│   └── static/
│
├── tools/                      # Outils et utilitaires
│   ├── r6-dissect.exe         # Parser de fichiers .rec
│   ├── parse_all.sh
│   └── scripts/               # Scripts batch hérités
│       ├── analyze_match_gui.bat
│       ├── analyze_match_simple.bat
│       ├── clean.bat
│       └── install.bat
│
├── data/                       # Données (ignoré par Git)
│   ├── uploads/               # Fichiers .rec uploadés
│   ├── match_data/            # JSON temporaires
│   └── reports/               # Rapports Excel générés
│
└── docs/                       # Documentation
    ├── CHANGELOG.md
    ├── LICENSE
    └── ...
```

## 🎯 Fonctionnalités

### Interface Web
- ✅ Drag & drop de fichiers .rec
- ✅ Upload multiple de fichiers
- ✅ Barre de progression en temps réel
- ✅ Liste des rapports générés
- ✅ Téléchargement direct des rapports
- ✅ Design responsive

### Analyse
- ✅ Parse automatique de tous les rounds
- ✅ Gestion des erreurs r6-dissect
- ✅ Nettoyage automatique des données temporaires
- ✅ Rapports horodatés pour historique
- ✅ Statistiques ATK/DEF/GLOBAL séparées

### Rapports Excel
- ✅ Mise en forme professionnelle
- ✅ Couleurs par équipe (bleu/rouge)
- ✅ En-têtes colorés ATK/DEF
- ✅ Timeline des kills avec headshots surlignés
- ✅ Colonnes auto-ajustées
- ✅ En-têtes figés

## 🔧 Configuration Avancée

### Changer le port du serveur

Éditez `web/app.py` ligne finale :

```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Changez 5000 en 8080
```

### Utiliser les anciens scripts batch

Les scripts d'origine sont toujours disponibles dans `tools/scripts/` :

- `analyze_match_gui.bat` : Interface avec fenêtres
- `analyze_match_simple.bat` : Interface avec saisie manuelle
- `clean.bat` : Nettoyage des fichiers temporaires

## 🐛 Troubleshooting

### L'interface web ne s'ouvre pas

1. Vérifiez que Python est installé : `python --version`
2. Installez Flask manuellement : `pip install flask`
3. Lancez manuellement : `python web/app.py`

### Erreur "r6-dissect.exe introuvable"

Vérifiez que `r6-dissect.exe` est bien dans le dossier `tools/`

### Erreur lors du parsing

Certains opérateurs récents peuvent ne pas être reconnus par r6-dissect. Les rounds affectés sont automatiquement ignorés.

### Port 5000 déjà utilisé

Changez le port dans `web/app.py` (voir Configuration Avancée)

## 📋 Prérequis

- **Windows 10/11** (64-bit)
- **Python 3.7+** ([télécharger](https://www.python.org/downloads/))
- **Navigateur web moderne** (Chrome, Firefox, Edge)

## 🛠️ Technologies

- **Backend** : Flask (Python)
- **Frontend** : HTML5, CSS3, JavaScript (Vanilla)
- **Analyse** : pandas, openpyxl
- **Parser** : r6-dissect v0.24.0 (Go)

## ⚠️ Limitations

- r6-dissect v0.24.0 peut ne pas reconnaître tous les opérateurs de Y10S4_01
- Taille maximale de fichier : 500MB
- Les fichiers .rec doivent être au format Dissect de Ubisoft

## 🔄 Mise à Jour

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

Pour mettre à jour r6-dissect, téléchargez la dernière version depuis [GitHub Releases](https://github.com/redraskal/r6-dissect/releases) et remplacez dans `tools/`.

## 📜 Licence

Projet privé - Tous droits réservés

## 🙏 Crédits

- **[redraskal](https://github.com/redraskal)** - Créateur de r6-dissect
- **Communauté R6** - Contributions et feedback

---

**Créé avec ❤️ pour améliorer votre jeu Rainbow Six Siege**

🌐 **Interface Web** • 📊 **Statistiques Pro** • 🎯 **Analyse Complète**
