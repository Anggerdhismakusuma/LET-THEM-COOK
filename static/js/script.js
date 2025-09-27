document.getElementById('imageInput').addEventListener('change', function(event) {
    const [file] = event.target.files;
    const preview = document.getElementById('imagePreview');
    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
    }
});

function uploadImage() {
    const fileInput = document.getElementById('imageInput');
    const resultOutput = document.getElementById('resultOutput');
    const loading = document.getElementById('loading');
    
    // Periksa apakah ada file yang dipilih
    if (fileInput.files.length === 0) {
        alert("Mohon pilih gambar terlebih dahulu.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    // Penting: Kunci harus 'file' agar sesuai dengan Flask API Anda (request.files['file'])
    formData.append('file', file);

    // Tampilkan loading dan bersihkan hasil
    resultOutput.innerHTML = '<p>Mengirim gambar ke API...</p>';
    loading.style.display = 'block';

    fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        loading.style.display = 'none';
        displayResult(data);
    })
    .catch(error => {
        loading.style.display = 'none';
        console.error('Error:', error);
        resultOutput.innerHTML = `<p style="color: red;">ERROR: Gagal menghubungi API atau terjadi kesalahan server. Cek konsol dan pastikan 'app.py' berjalan.</p>`;
    });
}

function displayResult(data) {
    const output = document.getElementById('resultOutput');
    
    if (data.status === 'success') {
        output.innerHTML = `
            <div class="result-item">
                <h3>🍽️ Hasil Prediksi: ${data.prediksi_nama}</h3>
                <p><strong>Tingkat Keyakinan:</strong> ${(data.akurasi_prediksi * 100).toFixed(2)}%</p>
                <hr>
                
                <h4>🔥 Informasi Gizi</h4>
                <p><strong>Kalori per Sajian:</strong> ${data.kalori_per_sajian}</p>
                
                <h4>📝 Resep dan Bahan</h4>
                <p><strong>Bahan Utama:</strong> ${data.bahan_utama}</p>
                <p><strong>Cara Membuat:</strong> ${data.cara_membuat.replace(/\n/g, '<br>')}</p>
            </div>
        `;
    } else {
        output.innerHTML = `<p style="color: red;">Prediksi gagal: ${data.error}</p>`;
    }
}