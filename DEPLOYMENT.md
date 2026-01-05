# 🚀 Panduan Deployment Aplikasi E-Raport

Panduan lengkap untuk deploy aplikasi e-raport menggunakan Docker, Nginx, dan SSL dengan Let's Encrypt.

## 📋 Prerequisites

1. **Server/VPS** dengan Ubuntu/Debian (minimal 1GB RAM)
2. **Docker** dan **Docker Compose** terinstall
3. **Domain** yang sudah pointing ke IP server
4. **Port 80 dan 443** terbuka di firewall

---

## 🔧 Instalasi Docker (jika belum ada)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Tambahkan user ke docker group (opsional)
sudo usermod -aG docker $USER
```

Logout dan login kembali untuk apply group permission.

---

## 📦 Step 1: Persiapan Aplikasi

### 1.1 Clone atau Upload Aplikasi

```bash
# Clone dari Git
git clone <repository-url> raport-app
cd raport-app

# Atau upload folder aplikasi ke server
```

### 1.2 Setup Environment Variables

```bash
# Copy file .env.example
cp .env.example .env

# Edit file .env
nano .env
```

**Isi .env dengan konfigurasi Anda:**

```env
# Flask Configuration
FLASK_CONFIG=production
SECRET_KEY=generate-random-key-di-sini-minimal-32-karakter

# Domain Configuration
DOMAIN=raport.sekolah.id
EMAIL=admin@sekolah.id
```

**Generate Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 1.3 Set Permission untuk Script

```bash
chmod +x setup-ssl.sh
```

---

## 🐳 Step 2: Jalankan Aplikasi dengan Docker

### 2.1 Build dan Start Containers

```bash
# Build dan jalankan semua services
docker-compose up -d --build

# Cek status containers
docker-compose ps
```

Output yang benar:
```
NAME                COMMAND                  SERVICE             STATUS              PORTS
raport_app          "gunicorn --bind 0.0…"   web                 running             
raport_certbot      "/bin/sh -c 'trap ex…"   certbot             running             
raport_nginx        "/docker-entrypoint.…"   nginx               running             0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### 2.2 Test Aplikasi (HTTP)

Buka browser dan akses: `http://YOUR_SERVER_IP`

Jika berhasil, Anda akan melihat halaman login aplikasi.

**Login Default:**
- Username: `admin`
- Password: `admin123`

> ⚠️ **PENTING:** Segera ubah password default setelah login pertama kali!

---

## 🔐 Step 3: Setup SSL Certificate

### 3.1 Pastikan Domain Sudah Pointing

Sebelum setup SSL, pastikan domain Anda sudah pointing ke IP server:

```bash
# Cek DNS resolution
nslookup raport.sekolah.id
# atau
dig raport.sekolah.id
```

### 3.2 Jalankan Script Setup SSL

```bash
./setup-ssl.sh
```

Script akan:
1. Request SSL certificate dari Let's Encrypt
2. Update Nginx configuration untuk HTTPS
3. Restart Nginx dengan SSL enabled

### 3.3 Test HTTPS

Buka browser dan akses: `https://YOUR_DOMAIN`

Semua traffic HTTP akan otomatis redirect ke HTTPS.

---

## 📊 Step 4: Monitoring dan Maintenance

### 4.1 Lihat Logs

```bash
# Semua logs
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f certbot
```

### 4.2 Restart Services

```bash
# Restart semua
docker-compose restart

# Restart specific service
docker-compose restart web
docker-compose restart nginx
```

### 4.3 Stop Services

```bash
docker-compose stop
```

### 4.4 Update Aplikasi

```bash
# Pull latest code
git pull

# Rebuild dan restart
docker-compose up -d --build
```

---

## 🔄 SSL Certificate Auto-Renewal

Certificate Let's Encrypt akan **otomatis di-renew** oleh Certbot container setiap 12 jam.

**Manual renewal (jika diperlukan):**
```bash
docker-compose run --rm certbot renew
docker-compose restart nginx
```

---

## 🗄️ Backup dan Restore

### Backup Database

```bash
# Backup database SQLite
docker-compose exec web cp /app/storage/data.sqlite /app/storage/backup-$(date +%Y%m%d).sqlite

# Copy backup ke local
docker cp raport_app:/app/storage/backup-20260105.sqlite ./backup/
```

### Restore Database

```bash
# Upload backup ke server
docker cp ./backup/data.sqlite raport_app:/app/storage/data.sqlite

# Restart aplikasi
docker-compose restart web
```

---

## 🛠️ Troubleshooting

### Container tidak running

```bash
# Cek logs untuk error
docker-compose logs

# Restart semua containers
docker-compose down
docker-compose up -d
```

### SSL Certificate gagal

**Checklist:**
1. ✅ Domain sudah pointing ke server IP
2. ✅ Port 80 dan 443 terbuka
3. ✅ Nginx container running
4. ✅ Email valid di .env

```bash
# Test manual
docker-compose run --rm certbot certonly --dry-run \
    --webroot --webroot-path=/var/www/certbot \
    -d YOUR_DOMAIN
```

### Database error

```bash
# Reset database (HATI-HATI: menghapus semua data!)
docker-compose down
rm -rf storage/data.sqlite
docker-compose up -d
```

### Permission denied di storage

```bash
# Fix permissions
sudo chown -R 1000:1000 storage/
docker-compose restart web
```

---

## 🔒 Security Best Practices

1. **Ubah Default Password** segera setelah login pertama
2. **Update Secret Key** di `.env` dengan value random
3. **Backup Database** secara berkala
4. **Update Dependencies** secara rutin:
   ```bash
   docker-compose pull
   docker-compose up -d --build
   ```
5. **Monitor Logs** untuk aktivitas mencurigakan
6. **Setup Firewall** (UFW):
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

---

## 📞 Support

Jika mengalami masalah, cek:
1. Logs: `docker-compose logs -f`
2. Container status: `docker-compose ps`
3. Nginx config syntax: `docker-compose exec nginx nginx -t`

---

## 📝 Catatan Penting

- **Database:** Aplikasi menggunakan SQLite (sesuai untuk skala kecil-menengah)
- **Storage:** File uploads disimpan di `./storage/`
- **Session:** Pastikan SECRET_KEY konsisten untuk session persistence
- **Certificate:** Auto-renew setiap 60 hari oleh Certbot

---

**Selamat! Aplikasi E-Raport Anda sekarang sudah online dengan HTTPS! 🎉**
