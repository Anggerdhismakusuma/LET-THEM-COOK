// --- FUNGSI BARU UNTUK FORMAT BAHAN UTAMA ---
function formatIngredientsList(ingredientsText) {
    if (!ingredientsText || ingredientsText === 'Data tidak tersedia') {
        return `<p>${ingredientsText}</p>`;
    }
    
    // 1. Pecah string bahan berdasarkan koma (,)
    // 2. filter(item => item.trim() !== '') untuk menghapus item kosong
    const items = ingredientsText.split(',').filter(item => item.trim() !== '');

    // Buat daftar tak bernomor (Unordered List: <ul>)
    let htmlList = '<ul class="ingredients-list">';
    
    items.forEach(item => {
        // Trim() untuk menghapus spasi di awal/akhir setiap item
        htmlList += `<li>${item.trim()}</li>`;
    });

    htmlList += '</ul>';
    return htmlList;
}

// --- Fungsi untuk Memformat Resep (Tidak Berubah) ---
function formatRecipeSteps(recipeText) {
    if (!recipeText || recipeText === 'Resep belum ditambahkan.') {
        return `<p>${recipeText}</p>`;
    }
    
    const steps = recipeText.split('\n').filter(step => step.trim() !== '');

    let htmlList = '<ol class="recipe-list">';
    
    steps.forEach(step => {
        const cleanStep = step.replace(/^\s*\d+\.\s*/, '');
        htmlList += `<li>${cleanStep}</li>`;
    });

    htmlList += '</ol>';
    return htmlList;
}

// --- FUNGSI UTAMA DISPLAY (Tidak Berubah, karena sudah memanggil fungsi di atas) ---
function displayResult(data) {
    const output = document.getElementById('resultOutput');
    
    if (data.status === 'success') {
        const confidencePercent = (parseFloat(data.akurasi_prediksi) * 100).toFixed(2);
        
        // Memanggil fungsi formatIngredientsList()
        const formattedIngredients = formatIngredientsList(data.bahan_utama);
        
        const formattedInstructions = formatRecipeSteps(data.cara_membuat);
        
        output.innerHTML = `
            <div class="result-item">
                <h4>🍽️ Prediksi: ${data.prediksi_nama}</h4>
                <p><strong>Tingkat Keyakinan Model:</strong> ${confidencePercent}%</p>
                
                <hr style="border-color: #50589C; margin: 15px 0;">
                
                <h4>🔥 Informasi Kalori</h4>
                <p><strong>Kalori per Sajian:</strong> ${data.kalori_per_sajian.replace(/&ndash;/g, '–')}</p>
                
                <h4>🥦 Bahan Utama</h4>
                ${formattedIngredients} 
                
                <h4>📝 Cara Membuat</h4>
                ${formattedInstructions} 
            </div>
        `;
    } else {
        output.innerHTML = `<p class="error-message">Prediksi gagal: ${data.error}</p>`;
    }
}

// --- Logika Input Gambar dan Upload (Tidak Berubah) ---

document.getElementById('imageInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('imagePreview');
    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }
});

function uploadImage() {
    const fileInput = document.getElementById('imageInput');
    const resultOutput = document.getElementById('resultOutput');
    const loading = document.getElementById('loading');
    
    if (fileInput.files.length === 0) {
        alert("Mohon pilih gambar makanan terlebih dahulu.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    resultOutput.innerHTML = '<p>Mengirim gambar dan menunggu prediksi...</p>';
    loading.style.display = 'block';

    fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        loading.style.display = 'none';
        displayResult(data);
    })
    .catch(error => {
        loading.style.display = 'none';
        console.error('Fetch Error:', error);
        resultOutput.innerHTML = `<p class="error-message">ERROR: Gagal menghubungi API (${error.message}). Pastikan server 'app.py' berjalan.</p>`;
    });
}