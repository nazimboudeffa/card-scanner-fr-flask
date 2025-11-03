from flask import Flask, render_template, request, jsonify
from PIL import Image
import imagehash
import sqlite3
import io

app = Flask(__name__)
DB_PATH = "database.db"

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
def find_closest_matches(image_hash, max_distance=10, limit=5):
    """
    Trouve les hashs les plus proches en calculant la distance de Hamming
    
    Args:
        image_hash: Le hash de l'image à comparer
        max_distance: Distance maximale pour considérer un match
        limit: Nombre maximum de résultats à retourner
    
    Returns:
        Liste de tuples (id, name, hash, distance) triés par distance
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, hash FROM cards")
    all_cards = c.fetchall()
    conn.close()
    
    # Convertir le hash en objet ImageHash pour calculer la distance
    input_hash = imagehash.hex_to_hash(image_hash)
    
    # Calculer la distance pour chaque carte
    distances = []
    for card_id, name, card_hash in all_cards:
        try:
            db_hash = imagehash.hex_to_hash(card_hash)
            distance = input_hash - db_hash  # Distance de Hamming
            if distance <= max_distance:
                distances.append({
                    'id': card_id,
                    'name': name,
                    'hash': card_hash,
                    'distance': distance
                })
        except Exception:
            continue
    
    # Trier par distance et limiter les résultats
    distances.sort(key=lambda x: x['distance'])
    return distances[:limit]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    try:
        hash_type = request.form.get("hash_type", "phash")
        hash_size = int(request.form.get("hash_size", 16))
        max_distance = int(request.form.get("max_distance", 50))  # Increased default
        limit = int(request.form.get("limit", 5))

        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image reçue'}), 400

        # Lecture de l'image uniquement en mémoire
        image = request.files['image']
        pil_img = Image.open(io.BytesIO(image.read()))

        # Calcul du hash
        image_hash = compute_hash(pil_img, hash_type=hash_type, hash_size=hash_size)

        # Comparaison avec la base - vérification exacte
        exact_match = hash_exists(image_hash)
        
        # Trouver les correspondances les plus proches
        closest_matches = find_closest_matches(image_hash, max_distance=max_distance, limit=limit)

        return jsonify({
            'exact_match': exact_match,
            'hash': image_hash,
            'hash_type': hash_type,
            'hash_size': hash_size,
            'closest_matches': closest_matches,
            'total_matches': len(closest_matches)
        })
    except Exception as e:
        app.logger.error(f"Error in /compare: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()  # Initialize database on startup
    app.run(host='0.0.0.0')