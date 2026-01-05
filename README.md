# Sistem Informasi Raport Digital (E-Raport) - Al Barokah

Aplikasi berbasis web untuk manajemen penilaian, data santri, dan pelaporan hasil belajar (raport) di Madrasah Diniyah Takmiliyah Al Barokah. Aplikasi ini dirancang untuk mempermudah administrasi akademik dengan antarmuka yang modern dan responsif.

## 📋 Fitur Utama

*   **Dashboard Statistik**: Ringkasan data santri, kelas, dan status sistem.
*   **Manajemen Data Santri**: Tambah, ubah, hapus, dan pencarian data santri.
*   **Input Nilai Akademik**: Pengisian nilai per mata pelajaran dan semester.
*   **Input Ekstrakurikuler**: Pencatatan kehadiran, kedisiplinan, dan catatan wali kelas.
*   **Cetak Raport**: Generasi raport otomatis siap cetak.
*   **Manajemen Database**:
    *   Backup & Restore data (mendukung backup per tahun ajar).
    *   Fitur "Zone Bahaya" untuk penghapusan data tahunan (Prune) atau reset total.
    *   Estimasi ukuran backup real-time.
*   **Pengaturan Sekolah**: Kustomisasi identitas madrasah, kepala sekolah, dan tahun ajaran.

## 🛠️ Persyaratan Sistem

### Development (Lokal)
*   **Python**: Versi 3.10 atau lebih baru.
*   **Sistem Operasi**: Windows, macOS, atau Linux.
*   **Browser**: Google Chrome, Mozilla Firefox, atau Microsoft Edge (terbaru).

### Production (Server)
*   **Server**: VPS/Cloud dengan minimal 1GB RAM
*   **Docker**: Version 20.10+
*   **Docker Compose**: Version 1.29+
*   **Domain**: Opsional (untuk SSL/HTTPS)

---

## 🚀 Quick Start

### 🐳 Deployment dengan Docker (Recommended)

**Paling mudah untuk production!** Aplikasi sudah include konfigurasi lengkap dengan Nginx dan SSL.

```bash
# 1. Clone repository
git clone <repository-url>
cd web_app

# 2. Jalankan setup wizard
chmod +x setup.sh
./setup.sh

# 3. Aplikasi sudah jalan!
# Akses: http://YOUR_DOMAIN atau http://YOUR_IP
```

**Setup SSL (jika punya domain):**
```bash
./setup-ssl.sh
```

📖 **Dokumentasi Lengkap:** [DEPLOYMENT.md](DEPLOYMENT.md) | [QUICK_START.md](QUICK_START.md)

---

## 💻 Development Lokal (Tanpa Docker)

### 1. Clone Repository
```bash
cd "d:\Project\Albarokah\Raport fix\web_app"
```

### 2. Buat Virtual Environment

**Windows:**
```bash
python -m venv env
env\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Instal Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi
```bash
python run.py
```

Akses: **http://localhost:5005**

### Akun Default
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **PENTING:** Segera ubah password setelah login pertama kali!

---

## 📚 Struktur Proyek

```
web_app/
├── app/
│   ├── core/              # Ekstensi inti (Database, Login Manager)
│   ├── models/            # Model Database (User, Student, Grade, dll)
│   ├── modules/           # Modul/Blueprint (Dashboard, Auth, Students, dll)
│   └── services/          # Layanan Logika Bisnis (Backup, Import)
├── storage/               # Database & Backup
├── web/
│   ├── static/            # Aset statis (CSS, JS, Gambar)
│   └── templates/         # File HTML (Jinja2)
├── nginx/                 # Nginx configuration
├── certbot/               # SSL certificates
├── config.py              # Konfigurasi Aplikasi
├── requirements.txt       # Dependensi Python
├── run.py                 # Entry point
├── Dockerfile             # Docker build
├── docker-compose.yml     # Production deployment
└── docker-compose.dev.yml # Development environment
```

---

## 🐳 Docker Commands

Jika menggunakan Docker, gunakan Makefile untuk kemudahan:

```bash
make help          # Show all available commands
make up            # Start production
make down          # Stop application
make logs          # View logs
make backup        # Backup database
make setup-ssl     # Setup SSL certificate
```

Atau gunakan docker-compose langsung:

```bash
docker-compose up -d       # Start
docker-compose logs -f     # View logs
docker-compose restart     # Restart
docker-compose down        # Stop
```

---

## 📦 Production Deployment

### Option 1: Docker (Recommended) ⭐

Lihat dokumentasi lengkap di [DEPLOYMENT.md](DEPLOYMENT.md)

**Quick Setup:**
```bash
# Setup environment
cp .env.example .env
nano .env  # Edit dengan konfigurasi Anda

# Start aplikasi
docker-compose up -d --build

# Setup SSL (jika punya domain)
./setup-ssl.sh
```

### Option 2: Manual (Tanpa Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Set production config
export FLASK_CONFIG=production

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 run:app
```

Kemudian setup Nginx sebagai reverse proxy manual.

---

## 🔒 Security Features

✅ HTTPS/SSL dengan Let's Encrypt (auto-renewal)  
✅ CSRF Protection  
✅ Secure Session Cookies  
✅ Password Hashing  
✅ SQL Injection Protection  
✅ Security Headers (HSTS, X-Frame-Options, dll)

---

## 🔧 Configuration

### Environment Variables (.env)

```env
FLASK_CONFIG=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:////app/storage/data.sqlite
DOMAIN=raport.sekolah.id
EMAIL=admin@sekolah.id
```

Generate secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🗄️ Database Backup

### Manual Backup
```bash
make backup
# atau
docker-compose exec web cp /app/storage/data.sqlite /app/storage/backups/backup.sqlite
```

### Automated Backup (Cron)
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/web_app && make backup
```

---

## 📖 Dokumentasi Tambahan

- [DEPLOYMENT.md](DEPLOYMENT.md) - Panduan deployment lengkap
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arsitektur sistem

---

## 🤝 Kontribusi

Jika Anda ingin berkontribusi pada pengembangan proyek ini:
1.  Fork repository ini.
2.  Buat branch fitur baru (`git checkout -b fitur-baru`).
3.  Commit perubahan Anda (`git commit -m 'Menambah fitur X'`).
4.  Push ke branch (`git push origin fitur-baru`).
5.  Buat Pull Request.

---

## 🆘 Troubleshooting

### Container tidak jalan
```bash
docker-compose logs -f
```

### Reset database
```bash
docker-compose down
rm storage/data.sqlite
docker-compose up -d
```

### SSL gagal
Pastikan:
- Domain sudah pointing ke server
- Port 80 & 443 terbuka
- Nginx container running

---

## 📞 Support

Untuk bantuan atau bug report, silakan buat issue di repository ini.

---

## 📄 Lisensi

Hak Cipta © 2024 - Madrasah Diniyah Takmiliyah Al Barokah.
Seluruh hak cipta dilindungi undang-undang. Penggunaan internal.
