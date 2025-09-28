import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from PIL import Image
import streamlit as st
import json
import io

# --- KONFIGURASI PATH ---
MODEL_PATH = 'models/mobilenet_ft_5cls_final.h5'
RECIPE_DB_PATH = 'recipes_db.json' 
IMAGE_SIZE = (224, 224)
CLASS_LABELS = ['apple_pie', 'baby_back_ribs', 'baklava', 'beef_carpaccio', 'beef_tartare'] 

st.set_page_config(
    page_title="Let Them Cook App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. MEMUAT MODEL DAN DATABASE (Gunakan st.cache_resource) ---
# st.cache_resource memastikan model hanya dimuat sekali, yang sangat penting untuk performa.
@st.cache_resource
def load_assets():
    try:
        # Memuat model Keras
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        st.success("[STATUS] Model berhasil dimuat.")
        
        # Memuat database resep
        with open(RECIPE_DB_PATH, 'r') as f:
            recipe_db = json.load(f)
        st.success("[STATUS] Database resep berhasil dimuat.")
        
        return model, recipe_db
        
    except Exception as e:
        st.error(f"[ERROR] Gagal memuat file yang dibutuhkan (model atau DB): {e}")
        st.stop() # Hentikan eksekusi Streamlit jika gagal memuat file
        return None, None

model, recipe_db = load_assets()

# --- 2. FUNGSI PRE-PROCESSING ---
def preprocess_image(uploaded_image_file):
    """Memproses file gambar yang diunggah Streamlit menjadi tensor siap prediksi."""
    # Membuka gambar dari file yang diunggah
    img = Image.open(uploaded_image_file)
    # Mengubah ukuran gambar
    img = img.resize(IMAGE_SIZE)
    
    # Mengubah ke array numpy dan menambahkan dimensi batch
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) # Shape: (1, 224, 224, 3)
    img_array /= 255.0 # Normalisasi (Wajib!)
    return img_array

# --- 3. FUNGSI PREDIKSI MURNI (Logic dari Flask API lama) ---
def get_prediction_and_recipe(model, processed_image_array, recipe_db, class_labels):
    """Melakukan prediksi dan mencari resep terkait."""
    
    predictions = model.predict(processed_image_array, verbose=0)
    predicted_index = np.argmax(predictions[0])
    
    predicted_name_key = class_labels[predicted_index]
    confidence = float(predictions[0][predicted_index])
    
    # Ambil data dari database resep
    food_data = recipe_db.get(predicted_name_key, {})
    
    # Bentuk hasil yang mudah ditampilkan Streamlit
    response = {
        'predicted_name': food_data.get('nama', predicted_name_key.replace('_', ' ').title()),
        'confidence': confidence,
        'calories': food_data.get('kalori_per_sajian', 'Data tidak tersedia'),
        'main_ingredients': food_data.get('bahan_utama', 'Data tidak tersedia'),
        'instructions': food_data.get('cara_membuat', 'Resep belum ditambahkan.')
    }
    return response

# =======================================================
# 4. INTERFACE STREAMLIT UTAMA
# =======================================================
st.title("👨‍🍳 Let Them Cook: Penemuan Resep Berbasis Gambar")

st.markdown("""
Aplikasi ini menggunakan Model MobileNet (5 kelas) untuk mengidentifikasi bahan makanan dan menyarankan resep.
""")

uploaded_file = st.file_uploader(
    "Upload gambar bahan makanan (JPG, JPEG, PNG)", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # Kolom untuk menampilkan gambar dan hasil
    col1, col2 = st.columns([1, 1.5])

    # Tampilkan Gambar
    with col1:
        st.subheader("Gambar Bahan Makanan")
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption=uploaded_file.name, use_column_width=True)

    # Tombol Prediksi
    with col2:
        if st.button("🍽️ Prediksi dan Cari Resep", use_container_width=True):
            with st.spinner('Sedang menganalisis gambar dan mencari resep...'):
                try:
                    # 1. Pre-process gambar
                    processed_array = preprocess_image(uploaded_file)
                    
                    # 2. Dapatkan Hasil Prediksi
                    result = get_prediction_and_recipe(model, processed_array, recipe_db, CLASS_LABELS)
                    
                    st.success("Analisis Selesai!")
                    
                    # 3. Tampilkan Hasil
                    st.subheader(f"Hasil Prediksi: {result['predicted_name']}")
                    st.metric(label="Tingkat Akurasi Model", value=f"{result['confidence']*100:.2f}%")
                    
                    st.markdown("---")
                    
                    st.caption("Detail Resep")
                    st.info(f"**Bahan Utama:** {result['main_ingredients']}")
                    st.warning(f"**Estimasi Kalori per Sajian:** {result['calories']}")
                    
                    st.markdown(f"**Cara Membuat:**\n{result['instructions']}")

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses data: {e}")


# --- KODE FLASK LAMA YANG SUDAH DIHAPUS:
# app = Flask(__name__)
# @app.route('/')
# def index():
#     return render_template('index.html')
# @app.route('/predict', methods=['POST'])
# def predict_food():
#     # ... semua logika di sini sudah dipindahkan ke get_prediction_and_recipe
#     ...
# if __name__ == '__main__':
#     app.run(...)