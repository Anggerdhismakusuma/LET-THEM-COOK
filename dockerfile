# 1. BASE IMAGE: Gunakan Python 3.10 slim, yang lebih kecil namun kompatibel dengan TensorFlow.
FROM python:3.10-slim

# 2. ENVIRONMENT VARIABLES: Set environment untuk optimasi Python dan Gunicorn.
# PYTHONDONTWRITEBYTECODE: Mencegah Python menulis file .pyc (mengurangi ukuran)
# PYTHONUNBUFFERED: Memastikan output log langsung muncul (penting untuk debugging)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_ENV production

# 3. WORK DIRECTORY: Tetapkan /app sebagai direktori kerja utama di dalam container.
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libjpeg-dev \
        zlib1g-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. INSTALL PYTHON DEPENDENCIES: Instal paket Python.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. COPY PROJECT FILES: Salin sisa kode proyek ke dalam container.
# Ini mencakup app.py, models/, static/, templates/, recipes_db.json, dll.
COPY . /app/

# 6. EXPOSE PORT: Beri tahu Docker bahwa aplikasi berjalan di port 5000.
EXPOSE 5000

# 7. START COMMAND: Perintah yang dijalankan saat container dimulai.
# Menggunakan Gunicorn sebagai server produksi:
# -w 4: Menggunakan 4 worker (sesuaikan dengan jumlah core CPU server)
# -b 0.0.0.0:5000: Binding ke semua antarmuka di port 5000
# app:app: Menunjuk ke variabel aplikasi 'app' di dalam file app.py
CMD ["python", "-m", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]