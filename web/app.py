"""
R6 Siege Match Stats Analyzer - Web Interface
Server Flask pour l'interface web avec auto-detection des replays
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import subprocess
import json
import shutil
from datetime import datetime
from pathlib import Path
import zipfile
import string
import re

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'uploads')
app.config['MATCH_DATA_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'match_data')
app.config['REPORTS_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'reports')
app.config['CONFIG_FILE'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'config.json')

# Creer les dossiers s'ils n'existent pas
for folder in [app.config['UPLOAD_FOLDER'], app.config['MATCH_DATA_FOLDER'], app.config['REPORTS_FOLDER']]:
    os.makedirs(folder, exist_ok=True)


def load_config():
    """Charger la configuration depuis le fichier JSON"""
    try:
        if os.path.exists(app.config['CONFIG_FILE']):
            with open(app.config['CONFIG_FILE'], 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement de la config: {e}")
    return {"game_path": None, "replay_path": None}


def save_config(config):
    """Sauvegarder la configuration dans le fichier JSON"""
    try:
        with open(app.config['CONFIG_FILE'], 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] Erreur lors de la sauvegarde de la config: {e}")
        return False


def detect_game_path():
    """Detecter automatiquement le chemin d'installation du jeu sur tous les disques"""
    found_paths = []

    # Scanner tous les disques disponibles
    for drive in string.ascii_uppercase:
        drive_path = f"{drive}:\\"
        if not os.path.exists(drive_path):
            continue

        # Chemins Ubisoft Connect
        ubisoft_paths = [
            f"{drive}:\\Program Files\\Ubisoft\\Ubisoft Game Launcher\\games\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Program Files (x86)\\Ubisoft\\Ubisoft Game Launcher\\games\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Ubisoft\\Ubisoft Game Launcher\\games\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Games\\Ubisoft\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Ubisoft Games\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Games\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Ubisoft\\games\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Program Files\\Ubisoft Games\\Tom Clancy's Rainbow Six Siege",
        ]

        # Chemins Steam
        steam_paths = [
            f"{drive}:\\Program Files\\Steam\\steamapps\\common\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Program Files (x86)\\Steam\\steamapps\\common\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Steam\\steamapps\\common\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\SteamLibrary\\steamapps\\common\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Games\\Steam\\steamapps\\common\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Games\\SteamLibrary\\steamapps\\common\\Tom Clancy's Rainbow Six Siege",
        ]

        # Chemins Epic Games
        epic_paths = [
            f"{drive}:\\Program Files\\Epic Games\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Program Files (x86)\\Epic Games\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Epic Games\\Tom Clancy's Rainbow Six Siege",
            f"{drive}:\\Games\\Epic Games\\Tom Clancy's Rainbow Six Siege",
        ]

        all_paths = ubisoft_paths + steam_paths + epic_paths

        for path in all_paths:
            if os.path.exists(path):
                replay_path = os.path.join(path, "MatchReplay")
                if os.path.exists(replay_path):
                    found_paths.append(path)

    # Retourner le premier trouve, ou None
    return found_paths[0] if found_paths else None


def get_available_stats():
    """Retourner la liste des categories de stats disponibles"""
    return {
        'kills': {'label': 'Kills / Deaths / K/D', 'default': True},
        'kost': {'label': 'KOST %', 'default': True},
        'survival': {'label': 'Survie (temps, rounds)', 'default': True},
        'headshots': {'label': 'Headshots / HS%', 'default': True},
        'opening': {'label': 'Opening Kills/Deaths', 'default': True},
        'multikills': {'label': 'Multi-kills', 'default': True},
        'plants': {'label': 'Plantes / Defuses', 'default': True},
        'teamkills': {'label': 'Teamkills', 'default': False},
        'rating': {'label': 'Rating', 'default': True},
    }


def get_match_metadata(match_dir):
    """Extraire les metadonnees d'un match depuis le premier fichier .rec"""
    rec_files = sorted([f for f in os.listdir(match_dir) if f.endswith('.rec')])

    if not rec_files:
        return None

    # Chemin vers r6-dissect.exe
    tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
    r6_dissect = os.path.join(tools_dir, 'r6-dissect.exe')

    if not os.path.exists(r6_dissect):
        return None

    # Parser le premier fichier pour les metadonnees
    first_rec = os.path.join(match_dir, rec_files[0])
    temp_json = os.path.join(app.config['MATCH_DATA_FOLDER'], 'temp_metadata.json')

    try:
        result = subprocess.run(
            [r6_dissect, first_rec, '-o', temp_json],
            capture_output=True,
            text=True,
            timeout=30
        )

        if not os.path.exists(temp_json) or os.path.getsize(temp_json) == 0:
            return None

        with open(temp_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Nettoyer le fichier temporaire
        os.remove(temp_json)

        # Extraire les informations
        map_name = data.get('map', {}).get('name', 'Unknown')
        match_type_raw = data.get('matchType', {}).get('name', 'Unknown')
        match_type_id = data.get('matchType', {}).get('id', 0)
        timestamp = data.get('timestamp', '')

        # Nombre de rounds (fichiers .rec)
        num_rounds = len(rec_files)

        # Classification du type de match
        if match_type_id == 2 or (num_rounds >= 4 and num_rounds <= 9):
            match_category = 'ranked'
        elif num_rounds == 12:
            match_category = 'scrim'
        else:
            match_category = 'custom'

        # Parser le timestamp du nom de dossier (Match-YYYY-MM-DD_HH-MM-SS-XX)
        folder_name = os.path.basename(match_dir)
        match_date = None
        match_pattern = re.match(r'Match-(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})', folder_name)
        if match_pattern:
            date_str = match_pattern.group(1)
            time_str = f"{match_pattern.group(2)}:{match_pattern.group(3)}:{match_pattern.group(4)}"
            match_date = f"{date_str} {time_str}"

        return {
            'folder': folder_name,
            'path': match_dir,
            'map': map_name,
            'matchType': match_type_raw,
            'matchCategory': match_category,
            'numRounds': num_rounds,
            'date': match_date or timestamp,
            'timestamp': timestamp
        }

    except Exception as e:
        print(f"[ERROR] Erreur lors de l'extraction des metadonnees: {e}")
        return None


@app.route('/')
def index():
    """Page principale avec interface"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET', 'POST'])
def config_route():
    """GET: retourne config actuelle ou null si premier lancement
       POST: sauvegarde le chemin du jeu, detecte MatchReplay"""

    if request.method == 'GET':
        config = load_config()
        return jsonify(config)

    elif request.method == 'POST':
        data = request.get_json()
        game_path = data.get('game_path')

        if not game_path:
            return jsonify({'error': 'Chemin du jeu requis'}), 400

        if not os.path.exists(game_path):
            return jsonify({'error': 'Le chemin specifie n\'existe pas'}), 400

        # Detecter le dossier MatchReplay
        replay_path = os.path.join(game_path, 'MatchReplay')

        if not os.path.exists(replay_path):
            return jsonify({'error': 'Dossier MatchReplay introuvable dans le chemin specifie'}), 400

        config = {
            'game_path': game_path,
            'replay_path': replay_path
        }

        if save_config(config):
            return jsonify({'success': True, 'config': config})
        else:
            return jsonify({'error': 'Erreur lors de la sauvegarde'}), 500


@app.route('/api/detect-game')
def detect_game():
    """Detecter automatiquement le chemin du jeu"""
    detected_path = detect_game_path()

    if detected_path:
        return jsonify({'found': True, 'path': detected_path})
    else:
        return jsonify({'found': False, 'path': None})


@app.route('/api/stats-options')
def stats_options():
    """Retourner les options de stats disponibles"""
    return jsonify(get_available_stats())


@app.route('/api/replays')
def list_replays():
    """Scanner le dossier MatchReplay et retourner la liste des matchs"""
    config = load_config()

    if not config.get('replay_path'):
        return jsonify({'error': 'Configuration non effectuee', 'needsSetup': True}), 400

    replay_path = config['replay_path']

    if not os.path.exists(replay_path):
        return jsonify({'error': 'Dossier MatchReplay introuvable'}), 404

    matches = []

    # Scanner tous les dossiers Match-*
    try:
        for item in os.listdir(replay_path):
            item_path = os.path.join(replay_path, item)

            if os.path.isdir(item_path) and item.startswith('Match-'):
                metadata = get_match_metadata(item_path)

                if metadata:
                    matches.append(metadata)
    except Exception as e:
        print(f"[ERROR] Erreur lors du scan: {e}")
        return jsonify({'error': f'Erreur lors du scan: {str(e)}'}), 500

    # Trier par date (plus recent en premier)
    matches.sort(key=lambda x: x.get('date', ''), reverse=True)

    return jsonify({
        'matches': matches,
        'total': len(matches),
        'replay_path': replay_path
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_matches():
    """Analyser les matchs selectionnes"""
    try:
        data = request.get_json()
        selected_matches = data.get('matches', [])
        stats_options = data.get('stats', {})

        if not selected_matches:
            return jsonify({'error': 'Aucun match selectionne'}), 400

        # Construire la liste des stats a inclure
        enabled_stats = []
        for stat_key, stat_info in get_available_stats().items():
            if stats_options.get(stat_key, stat_info['default']):
                enabled_stats.append(stat_key)

        print(f"\n[DEBUG] Analyse de {len(selected_matches)} match(s)")
        print(f"[DEBUG] Stats activees: {enabled_stats}")

        reports = []

        for match_info in selected_matches:
            match_path = match_info.get('path')

            if not match_path or not os.path.exists(match_path):
                continue

            print(f"[DEBUG] Traitement de: {match_info.get('folder')}")

            # Nettoyer les anciens JSON
            for file in os.listdir(app.config['MATCH_DATA_FOLDER']):
                filepath = os.path.join(app.config['MATCH_DATA_FOLDER'], file)
                if file.endswith('.json'):
                    os.unlink(filepath)

            # Chemin vers r6-dissect.exe
            tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
            r6_dissect = os.path.join(tools_dir, 'r6-dissect.exe')

            if not os.path.exists(r6_dissect):
                return jsonify({'error': 'r6-dissect.exe introuvable'}), 500

            # Parser tous les fichiers .rec du match
            rec_files = sorted([f for f in os.listdir(match_path) if f.endswith('.rec')])

            parsed_files = []
            for idx, rec_file in enumerate(rec_files, 1):
                rec_path = os.path.join(match_path, rec_file)
                json_filename = f"round{idx:02d}.json"
                json_path = os.path.join(app.config['MATCH_DATA_FOLDER'], json_filename)

                result = subprocess.run(
                    [r6_dissect, rec_path, '-o', json_path],
                    capture_output=True,
                    text=True
                )

                if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
                    parsed_files.append(json_filename)

            if not parsed_files:
                continue

            # Generer le nom de sortie
            # Format: Map_DateGame_Type_DateAnalyse.xlsx
            map_name = match_info.get('map', 'Unknown').replace(' ', '-')
            match_category = match_info.get('matchCategory', 'custom').capitalize()

            # Date du match
            match_date = match_info.get('date', '')
            if match_date:
                try:
                    dt = datetime.strptime(match_date, '%Y-%m-%d %H:%M:%S')
                    date_game = dt.strftime('%Y-%m-%d')
                except:
                    date_game = match_date.split(' ')[0] if ' ' in match_date else match_date[:10]
            else:
                date_game = 'Unknown'

            # Date d'analyse
            date_analyse = datetime.now().strftime('%Y-%m-%d_%H-%M')

            output_name = f"{map_name}_{date_game}_{match_category}_{date_analyse}.xlsx"

            # Executer le script d'analyse Python
            src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
            analyze_script = os.path.join(src_dir, 'analyze_match_complete.py')

            # Changer temporairement le repertoire de travail
            original_dir = os.getcwd()
            project_root = os.path.dirname(os.path.dirname(__file__))
            os.chdir(project_root)

            # Construire la commande avec les options de stats
            cmd = [sys.executable, analyze_script, '--output-name', output_name]
            if enabled_stats:
                cmd.extend(['--stats', ','.join(enabled_stats)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            os.chdir(original_dir)

            if result.returncode != 0:
                print(f"[ERROR] Erreur analyse: {result.stderr}")
                continue

            # Deplacer le rapport vers le dossier reports
            source_path = os.path.join(project_root, output_name)

            if os.path.exists(source_path):
                dest_path = os.path.join(app.config['REPORTS_FOLDER'], output_name)
                shutil.move(source_path, dest_path)

                reports.append({
                    'filename': output_name,
                    'match': match_info.get('folder'),
                    'rounds': len(parsed_files)
                })

        if not reports:
            return jsonify({'error': 'Aucun match analyse avec succes'}), 500

        return jsonify({
            'success': True,
            'reports': reports,
            'total': len(reports)
        })

    except Exception as e:
        import traceback
        print(f"[ERROR] Exception: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Erreur inattendue: {str(e)}'}), 500


@app.route('/upload', methods=['POST'])
def upload_files():
    """Upload des fichiers .rec via drag & drop (methode legacy)"""
    if 'files[]' not in request.files:
        return jsonify({'error': 'Aucun fichier trouve'}), 400

    files = request.files.getlist('files[]')

    if not files:
        return jsonify({'error': 'Aucun fichier selectionne'}), 400

    # Nettoyer les anciens uploads
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")

    # Sauvegarder les nouveaux fichiers
    uploaded_files = []
    for file in files:
        if file and file.filename.endswith('.rec'):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_files.append(filename)

    if not uploaded_files:
        return jsonify({'error': 'Aucun fichier .rec valide'}), 400

    return jsonify({
        'success': True,
        'files': uploaded_files,
        'count': len(uploaded_files)
    })


@app.route('/analyze', methods=['POST'])
def analyze_match():
    """Analyser les fichiers .rec uploades (methode legacy)"""
    try:
        print("\n[DEBUG] Debut de l'analyse")
        # Nettoyer les anciens JSON
        for file in os.listdir(app.config['MATCH_DATA_FOLDER']):
            filepath = os.path.join(app.config['MATCH_DATA_FOLDER'], file)
            if file.endswith('.json'):
                os.unlink(filepath)
        print(f"[DEBUG] Anciens JSON nettoyes")

        # Chemin vers r6-dissect.exe
        tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
        r6_dissect = os.path.join(tools_dir, 'r6-dissect.exe')
        print(f"[DEBUG] Chemin r6-dissect: {r6_dissect}")

        if not os.path.exists(r6_dissect):
            print("[ERROR] r6-dissect.exe introuvable!")
            return jsonify({'error': 'r6-dissect.exe introuvable'}), 500

        # Parser tous les fichiers .rec
        rec_files = sorted([f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.rec')])
        print(f"[DEBUG] Fichiers .rec trouves: {len(rec_files)}")

        if not rec_files:
            return jsonify({'error': 'Aucun fichier .rec a analyser'}), 400

        parsed_files = []
        for idx, rec_file in enumerate(rec_files, 1):
            rec_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_file)
            json_filename = f"round{idx:02d}.json"
            json_path = os.path.join(app.config['MATCH_DATA_FOLDER'], json_filename)

            # Parser avec r6-dissect
            result = subprocess.run(
                [r6_dissect, rec_path, '-o', json_path],
                capture_output=True,
                text=True
            )

            # Verifier que le JSON est valide (taille > 0)
            if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
                parsed_files.append(json_filename)

        if not parsed_files:
            print("[ERROR] Aucun fichier parse avec succes")
            return jsonify({'error': 'Aucun fichier parse avec succes'}), 500

        print(f"[DEBUG] {len(parsed_files)} fichiers parses avec succes")

        # Executer le script d'analyse Python
        src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
        analyze_script = os.path.join(src_dir, 'analyze_match_complete.py')
        print(f"[DEBUG] Script d'analyse: {analyze_script}")

        # Changer temporairement le repertoire de travail
        original_dir = os.getcwd()
        project_root = os.path.dirname(os.path.dirname(__file__))
        os.chdir(project_root)
        print(f"[DEBUG] Repertoire de travail change vers: {project_root}")

        result = subprocess.run(
            [sys.executable, analyze_script],
            capture_output=True,
            text=True
        )

        os.chdir(original_dir)
        print(f"[DEBUG] Code retour: {result.returncode}")

        if result.returncode != 0:
            print(f"[ERROR] Stderr: {result.stderr}")
            print(f"[ERROR] Stdout: {result.stdout}")
            return jsonify({
                'error': 'Erreur lors de l\'analyse',
                'details': result.stderr
            }), 500

        # Trouver le fichier Excel genere (le plus recent)
        project_root = os.path.dirname(os.path.dirname(__file__))
        excel_files = [f for f in os.listdir(project_root) if f.startswith('Match_Stats_Complete_') and f.endswith('.xlsx')]

        if not excel_files:
            return jsonify({'error': 'Aucun rapport Excel genere'}), 500

        # Prendre le plus recent
        latest_excel = sorted(excel_files)[-1]
        source_path = os.path.join(project_root, latest_excel)
        dest_path = os.path.join(app.config['REPORTS_FOLDER'], latest_excel)

        # Copier vers le dossier reports
        shutil.copy2(source_path, dest_path)

        return jsonify({
            'success': True,
            'report': latest_excel,
            'parsed_rounds': len(parsed_files)
        })

    except Exception as e:
        import traceback
        print(f"[ERROR] Exception inattendue: {str(e)}")
        print(f"[ERROR] Traceback:")
        traceback.print_exc()
        return jsonify({
            'error': f'Erreur inattendue: {str(e)}'
        }), 500


@app.route('/download/<filename>')
def download_report(filename):
    """Telecharger le rapport Excel genere"""
    filepath = os.path.join(app.config['REPORTS_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'Fichier introuvable'}), 404

    return send_file(filepath, as_attachment=True)


@app.route('/reports')
def list_reports():
    """Lister tous les rapports disponibles"""
    reports = []

    if os.path.exists(app.config['REPORTS_FOLDER']):
        for filename in os.listdir(app.config['REPORTS_FOLDER']):
            if filename.endswith('.xlsx'):
                filepath = os.path.join(app.config['REPORTS_FOLDER'], filename)
                reports.append({
                    'filename': filename,
                    'size': os.path.getsize(filepath),
                    'created': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                })

    # Trier par date de creation (plus recent en premier)
    reports.sort(key=lambda x: x['created'], reverse=True)

    return jsonify({'reports': reports})


if __name__ == '__main__':
    print("=" * 60)
    print(" R6 Siege Match Stats Analyzer - Interface Web")
    print("=" * 60)
    print("")
    print("Serveur demarre sur: http://localhost:5000")
    print("Auto-detection des replays R6 Siege")
    print("")
    print("Appuyez sur Ctrl+C pour arreter le serveur")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
