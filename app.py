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

# Initialise la base de données
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cards
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  file_path TEXT,
                  hash TEXT)''')
    conn.commit()
    conn.close()

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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM cards WHERE hash=?", (image_hash,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# Trouve les hashs les plus proches dans la base
def find_closest_match(image_hash, max_distance=10):
    """
    Trouve le hash le plus proche en calculant la distance de Hamming
    Args:
        image_hash: Le hash de l'image à comparer
        max_distance: Distance maximale pour considérer un match
    Returns:
        Un dict (id, name, hash, distance) du match le plus proche ou None
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, hash FROM cards")
    all_cards = c.fetchall()
    conn.close()

    input_hash = imagehash.hex_to_hash(image_hash)
    closest = None
    min_distance = None
    for card_id, name, card_hash in all_cards:
        try:
            db_hash = imagehash.hex_to_hash(card_hash)
            distance = input_hash - db_hash
            if distance <= max_distance:
                if min_distance is None or distance < min_distance:
                    min_distance = distance
                    closest = {
                        'id': int(card_id),
                        'name': name,
                        'hash': card_hash,
                        'distance': int(distance)
                    }
        except Exception:
            continue
    return closest

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
        pil_img = Image.open(io.BytesIO(image.read()))

        # Calcul du hash
        image_hash = compute_hash(pil_img, hash_type=hash_type, hash_size=hash_size)
        logger.info(f"Computed hash: {image_hash}, type: {hash_type}, size: {hash_size}")

        # Comparaison avec la base - vérification exacte
        exact_match = hash_exists(image_hash)
        
        # Trouver la correspondance la plus proche
        closest_match = find_closest_match(image_hash, max_distance=max_distance)
        
        if closest_match:
            logger.info(f"Closest match: {closest_match['name']} with distance {closest_match['distance']}")
        else:
            logger.info(f"No match found within max_distance {max_distance}")

        return jsonify({
            'exact_match': exact_match,
            'hash': image_hash,
            'hash_type': hash_type,
            'hash_size': hash_size,
            'closest_match': closest_match
        })
    except Exception as e:
        logger.error(f"Error in /compare: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()  # Initialize database on startup
    app.run(host='0.0.0.0', debug=True)