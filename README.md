# 🗞️ News Scraper

Proyek scraper berita otomatis untuk mengumpulkan artikel dari portal berita Galamedia (galamedia.pikiran-rakyat.com)

## 📋 Fitur Utama

- Pengambilan artikel berita secara otomatis
- Dukungan proxy untuk menghindari pembatasan akses
- Integrasi dengan MongoDB untuk penyimpanan data
- Penanganan kesalahan dan logging
- Parsing dan formatting tanggal
- Bypass Cloudflare menggunakan cloudscraper

## 🔧 Persyaratan Sistem

- Python 3.9+
- Server MongoDB
- Package Python yang diperlukan:

```pip
requests==2.31.0
cloudscraper==1.2.70
beautifulsoup4==4.12.2
python-dateutil==2.8.2
pymongo==4.6.1
urllib3==1.26.16
pytz==2023.3
python-dotenv==1.0.0
pysocks==1.7.1
```

## 🛠️ Cara Instalasi

1. Clone repository ini
2. Buat virtual environment (direkomendasikan):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Konfigurasi file 

.env

:
   ```env
   DB_PORTS = ['27017']
   DB_HOST = localhost:27017
   DB_USER = admin
   DB_PASS = admin123
   DB_NAME = onlinenews_datalake
   ```

## 📁 Struktur Proyek

```
├── .env                  # Variabel environment
├── galamedia.py         # Script utama scraper
├── model/
│   └── db.py           # Koneksi database
├── modules/
│   ├── fake_header.py  # Generator user-agent
│   ├── helper.py       # Utilitas formatting tanggal
│   └── proxy.py        # Manajemen proxy
└── requirements.txt     # Dependency proyek
```

## 🚀 Penggunaan

Jalankan scraper dengan perintah:

```bash
python galamedia.py
```

## 💾 Data yang Disimpan

Scraper akan menyimpan informasi berikut untuk setiap artikel:
- Judul
- Konten
- Tanggal publikasi
- Nama jurnalis
- URL thumbnail
- URL sumber
- Nama portal
- Timestamp

## 🔄 Dukungan Proxy

Fitur proxy meliputi:
- Pemilihan proxy secara acak
- Rotasi proxy
- Pencatatan proxy yang gagal
- Percobaan ulang otomatis

## 📊 Logging

Sistem mencatat:
- Sesi scraping
- Penggunaan proxy
- Error dan exception
- Metrik performa

## ⚠️ Penanganan Error

- Masalah koneksi
- Ketersediaan situs
- Error parsing
- Kegagalan proxy

## 👥 Kontribusi

Anda dapat:
- Melaporkan bug
- Mengajukan pull request
- Menyarankan perbaikan
- Menambahkan fitur baru

## 📝 Lisensi

Proyek ini bersifat open-source dan tersedia di bawah Lisensi MIT.

---
Dibuat dengan ❤️ untuk komunitas scraping Indonesia
