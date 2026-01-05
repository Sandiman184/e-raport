# 🚀 Quick Start - Deploy E-Raport

Panduan singkat untuk deploy aplikasi dalam 5 menit.

## Prerequisites
- Server Ubuntu/Debian dengan Docker terinstall
- Domain yang sudah pointing ke server
- Port 80 dan 443 terbuka

## Langkah Deploy

### 1️⃣ Setup Environment
```bash
# Copy dan edit .env
cp .env.example .env
nano .env
```

Edit nilai berikut di `.env`:
```env
SECRET_KEY=<generate-random-key-32-karakter>
DOMAIN=raport.sekolah.id  # Ganti dengan domain Anda
EMAIL=admin@sekolah.id     # Ganti dengan email Anda
```

**Generate Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2️⃣ Jalankan Aplikasi
```bash
# Build dan start
docker-compose up -d --build

# Cek status
docker-compose ps
```

### 3️⃣ Test HTTP (opsional)
Buka: `http://IP_SERVER_ANDA`

Login dengan:
- Username: `admin`
- Password: `admin123`

### 4️⃣ Setup SSL
```bash
# Pastikan domain sudah pointing!
# Cek dengan: nslookup YOUR_DOMAIN

# Jalankan setup SSL
chmod +x setup-ssl.sh
./setup-ssl.sh
```

### 5️⃣ Done! 🎉
Aplikasi sudah online di: `https://YOUR_DOMAIN`

---

## Perintah Berguna

```bash
# Lihat logs
docker-compose logs -f

# Restart aplikasi
docker-compose restart web

# Stop semua
docker-compose down

# Update aplikasi
git pull
docker-compose up -d --build
```

---

## Troubleshooting

**Container tidak jalan?**
```bash
docker-compose logs
```

**SSL gagal?**
- Pastikan domain pointing ke server
- Pastikan port 80 & 443 terbuka
- Cek: `nslookup YOUR_DOMAIN`

**Database error?**
```bash
docker-compose restart web
```

---

## 📚 Dokumentasi Lengkap
Lihat [DEPLOYMENT.md](DEPLOYMENT.md) untuk panduan lengkap.

---

**Login Default:**
- Username: `admin`
- Password: `admin123`

⚠️ **Segera ubah password setelah login pertama!**
