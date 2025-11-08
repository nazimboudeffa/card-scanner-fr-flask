from flask import Flask, render_template, request, jsonify
from PIL import Image
import imagehash
import sqlite3
import io
import logging

app = Flask(__name__)
DB_PATH = "database.db"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Open a read-only connection to the existing SQLite DB.

    Note: We do NOT create tables here. The DB is expected to already exist
    with the required schema (tables: hashs, cards).
    """
    # Standard connection (read/write). If you want read-only, use URI mode:
    # sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

# Calcule le hash perceptuel
def compute_hash(pil_img, hash_type="phash", hash_size=16):
    if hash_type == "phash":
        return str(imagehash.phash(pil_img, hash_size=hash_size))
    if hash_type == "dhash":
        return str(imagehash.dhash(pil_img, hash_size=hash_size))
    if hash_type == "ahash":
        return str(imagehash.average_hash(pil_img, hash_size=hash_size))
    if hash_type == "whash":
        return str(imagehash.whash(pil_img, hash_size=hash_size))
    raise ValueError("Type de hash inconnu")

# Vérifie si un hash existe dans la base
def hash_exists(image_hash):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT file_name FROM hashs WHERE hash=?", (image_hash,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# Trouve les hashs les plus proches dans la base
def find_closest_matches(image_hash, max_distance=10, limit=10):
    """
    Trouve les hashs les plus proches en calculant la distance de Hamming
    Args:
        image_hash: Le hash de l'image à comparer
        max_distance: Distance maximale pour considérer un match
        limit: Nombre maximum de résultats à retourner
    Returns:
        Une liste de dicts (id, name, hash, distance) triés par distance
    """
    conn = get_db_connection()
    c = conn.cursor()
    # Join hashs with cards on file_name to retrieve card infos along with stored hash
    c.execute(
        """
        SELECT h.hash, h.file_name, c.name_fr, c.set_code, c.rarity_fr
        FROM hashs h
        LEFT JOIN cards c ON c.file_name = h.file_name
        """
    )
    all_rows = c.fetchall()
    conn.close()

    input_hash = imagehash.hex_to_hash(image_hash)
    matches = []
    for card_hash, file_name, name_fr, set_name, rarity in all_rows:
        try:
            db_hash = imagehash.hex_to_hash(card_hash)
            distance = input_hash - db_hash
            if distance <= max_distance:
                matches.append({
                    # Keep a stable "name" key for frontend and logs
                    'name': name_fr,
                    'file_name': file_name,
                    'set_code': set_name,
                    'rarity_fr': rarity,
                    'hash': card_hash,
                    'distance': int(distance)
                })
        except Exception:
            continue
    
    # Sort by distance and limit results
    matches.sort(key=lambda x: x['distance'])
    return matches[:limit]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/compare', methods=['POST'])
def compare():
    try:
        hash_type = request.form.get("hash_type", "phash")
        hash_size = int(request.form.get("hash_size", 16))
        max_distance = int(request.form.get("max_distance", 150))  # Increased default for camera captures

        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image reçue'}), 400

        # Lecture de l'image uniquement en mémoire
        image = request.files['image']
        pil_img = Image.open(io.BytesIO(image.read())).convert("RGB").resize((400, 300))

        # Calcul du hash
        image_hash = compute_hash(pil_img, hash_type=hash_type, hash_size=hash_size)
        logger.info(f"Computed hash: {image_hash}, type: {hash_type}, size: {hash_size}")

        # Comparaison avec la base - vérification exacte
        exact_match = hash_exists(image_hash)
        
        # Trouver les correspondances les plus proches
        closest_matches = find_closest_matches(image_hash, max_distance=max_distance, limit=10)
        closest_match = closest_matches[0] if closest_matches else None
        
        if closest_match:
            logger.info(f"Closest match: {closest_match['name']} with distance {closest_match['distance']}")
            logger.info(f"Total matches found: {len(closest_matches)}")
        else:
            logger.info(f"No match found within max_distance {max_distance}")

        return jsonify({
            'exact_match': exact_match,
            'hash': image_hash,
            'hash_type': hash_type,
            'hash_size': hash_size,
            'closest_match': closest_match,
            'closest_matches': closest_matches,
            'total_matches': len(closest_matches)
        })
    except Exception as e:
        logger.error(f"Error in /compare: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Do NOT create or modify tables here; DB must already exist.
    app.run(host='0.0.0.0', debug=True)