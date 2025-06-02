# Menggunakan MongoDB dengan Distributed Hashcat Cracking System

Panduan ini menjelaskan cara menggunakan sistem dengan MongoDB yang sebenarnya, tanpa menggunakan mock database.

## Prasyarat

1. MongoDB terinstal dan berjalan di komputer Anda
2. Python 3.8+ dengan paket-paket yang diperlukan (lihat `requirements.txt`)

## Langkah-langkah Konfigurasi

### 1. Pastikan MongoDB Berjalan

```bash
# Periksa apakah MongoDB sudah berjalan
brew services list | grep mongodb

# Jika belum berjalan, jalankan MongoDB
brew services start mongodb-community
```

### 2. Konfigurasi File .env

File `.env` sudah dibuat dengan konfigurasi default. Pastikan parameter `USE_MOCK_DATABASE` diatur ke `false`:

```
# MongoDB settings
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=hashcat_cracking

# Server settings
SERVER_HOST=0.0.0.0
SERVER_PORT=8082

# Use real database instead of mock
USE_MOCK_DATABASE=false
```

### 3. Instal Dependensi MongoDB

Pastikan paket-paket Python yang diperlukan untuk MongoDB sudah terinstal:

```bash
pip install motor pymongo
```

## Menjalankan Sistem dengan MongoDB

1. Pastikan MongoDB berjalan
2. Jalankan server web:

```bash
python -m cmd.web --port 8082
```

Server akan otomatis terhubung ke MongoDB berdasarkan konfigurasi di file `.env`.

## Struktur Database MongoDB

Database MongoDB akan dibuat secara otomatis dengan koleksi-koleksi berikut:

- **tasks**: Menyimpan informasi tugas cracking
- **agents**: Menyimpan informasi agen yang terhubung
- **results**: Menyimpan hasil cracking

## Perbedaan dengan Mock Database

Saat menggunakan MongoDB yang sebenarnya:

1. Data akan disimpan secara permanen di database MongoDB
2. Sistem akan menggunakan implementasi repository dan usecase yang sebenarnya
3. Performa dan skalabilitas akan lebih baik untuk dataset besar
4. Fitur-fitur lanjutan seperti indeks dan agregasi dapat digunakan

## Kembali ke Mock Database

Jika ingin kembali menggunakan mock database, ubah parameter `USE_MOCK_DATABASE` di file `.env` menjadi `true`:

```
USE_MOCK_DATABASE=true
```

## Troubleshooting

### Tidak Dapat Terhubung ke MongoDB

Jika server tidak dapat terhubung ke MongoDB, periksa:

1. Apakah MongoDB berjalan (`brew services list | grep mongodb`)
2. Apakah URI MongoDB di file `.env` benar
3. Apakah port MongoDB (27017) tidak diblokir oleh firewall

### Data Tidak Tersimpan

Jika data tidak tersimpan dengan benar:

1. Periksa log server untuk pesan error
2. Gunakan MongoDB Compass untuk memeriksa koneksi dan data di database

## Memeriksa Data di MongoDB

Untuk memeriksa data yang tersimpan di MongoDB:

```bash
# Masuk ke shell MongoDB
mongosh

# Pilih database
use hashcat_cracking

# Lihat koleksi yang tersedia
show collections

# Lihat data tasks
db.tasks.find()

# Lihat data agents
db.agents.find()

# Lihat data results
db.results.find()
```

Atau gunakan MongoDB Compass untuk antarmuka grafis yang lebih mudah digunakan.
