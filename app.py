import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import io

# --- KONFIGURASI PATH ---
# Path relatif ke file di dalam struktur folder project
MODEL_PATH = 'models/mobilenet_ft_5cls_final.h5'
RECIPE_DB_PATH = 'recipes_db.json' 
IMAGE_SIZE = (224, 224)

# --- URUTAN KELAS KRITIS ---
# Ini HARUS SAMA PERSIS dengan urutan class_indices yang dihasilkan saat training!
CLASS_LABELS = ['apple_pie', 'baby_back_ribs', 'baklava', 'beef_carpaccio', 'beef_tartare'] 

# --- 1. MEMUAT MODEL DAN DATABASE ---
try:
    # Memuat model Keras
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"[STATUS] Model berhasil dimuat dari: {MODEL_PATH}")
    
    # Memuat database resep
    with open(RECIPE_DB_PATH, 'r') as f:
        recipe_db = json.load(f)
    print(f"[STATUS] Database resep berhasil dimuat dari: {RECIPE_DB_PATH}")
    
except Exception as e:
    print(f"[ERROR] Gagal memuat file: {e}")
    # Hentikan aplikasi jika model atau DB tidak dapat dimuat
    exit()

app = Flask(__name__)
CORS(app)

# --- 2. FUNGSI PRE-PROCESSING ---
def preprocess_image(img_stream):
    """Memproses stream gambar dari request menjadi tensor siap prediksi."""
    # load_img menerima stream data menggunakan io.BytesIO(img_stream.read())
    img = image.load_img(io.BytesIO(img_stream.read()), target_size=IMAGE_SIZE)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) # Tambahkan dimensi batch (1, 224, 224, 3)
    img_array /= 255.0 # Normalisasi (Wajib!)
    return img_array

# --- 3. ENDPOINT API PREDIKSI ---
@app.route('/')
def index():
    # Ini mencari file index.html di folder 'templates'
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_food():
    """Menerima gambar, memprediksi kelas, dan mengembalikan resep terkait."""
    
    # Validasi file input
    if 'file' not in request.files:
        return jsonify({'error': 'Parameter "file" tidak ditemukan dalam request.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Tidak ada file yang dipilih.'}), 400

    try:
        # Pre-process gambar dari stream
        processed_image = preprocess_image(file)
        
        # Prediksi
        predictions = model.predict(processed_image)
        predicted_index = np.argmax(predictions[0])
        
        predicted_name_key = CLASS_LABELS[predicted_index]
        confidence = float(predictions[0][predicted_index])
        
        # Ambil data dari database resep
        food_data = recipe_db.get(predicted_name_key, {})
        
        # Bentuk respon akhir
        response = {
            'status': 'success',
            'prediksi_nama': food_data.get('nama', predicted_name_key.replace('_', ' ').title()),
            'akurasi_prediksi': f"{confidence:.4f}",
            'kalori_per_sajian': food_data.get('kalori_per_sajian', 'Data tidak tersedia'),
            'bahan_utama': food_data.get('bahan_utama', 'Data tidak tersedia'),
            'cara_membuat': food_data.get('cara_membuat', 'Resep belum ditambahkan.')
        }

        return jsonify(response)
        
    except Exception as e:
        # Menangkap error umum selama pemrosesan/prediksi
        return jsonify({'error': f'Terjadi kesalahan internal saat memproses gambar: {e}'}), 500


# --- 4. JALANKAN APLIKASI ---
if __name__ == '__main__':
    # Anda mungkin perlu menginstal semua requirements.txt terlebih dahulu: pip install -r requirements.txt
    print("\n--- Menjalankan Flask API ---")
    print("API berjalan di: http://127.0.0.1:5000/")
    app.run(host='0.0.0.0', port=5000, debug=False)