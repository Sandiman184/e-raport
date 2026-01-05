# 🚀 Production Deployment Guide - e-raport-albarokah.online

Panduan lengkap untuk deploy aplikasi E-Raport ke production dengan domain **e-raport-albarokah.online**.

---

## 📋 Overview

Panduan ini akan membantu Anda:
1. ✅ Setup VPS/Server
2. ✅ Konfigurasi DNS pointing
3. ✅ Deploy aplikasi dengan Docker
4. ✅ Setup SSL/HTTPS dengan Let's Encrypt
5. ✅ Configuration security dan monitoring

**Estimasi waktu:** 30-60 menit

---

## 🎯 Domain Configuration

**Domain:** e-raport-albarokah.online  
**Access:** https://e-raport-albarokah.online  
**Admin Email:** admin@e-raport-albarokah.online

---

## 🖥️ Step 1: Persiapan Server VPS

### A. Rekomendasi VPS Provider

| Provider | Harga/Bulan | RAM | Storage | Bandwidth |
|----------|-------------|-----|---------|-----------|
| **DigitalOcean** | $6 | 1GB | 25GB SSD | 1TB |
| **Vultr** | $6 | 1GB | 25GB SSD | 1TB |
| **Linode** | $5 | 1GB | 25GB SSD | 1TB |
| **AWS Lightsail** | $5 | 1GB | 40GB SSD | 2TB |

**Lokasi Server:** Pilih Singapore untuk Indonesia (latency rendah)

### B. OS yang Disarankan

- **Ubuntu 22.04 LTS** (RECOMMENDED)
- Ubuntu 20.04 LTS
- Debian 11

### C. SSH ke Server

Setelah beli VPS, Anda akan dapat:
- **IP Address:** contoh `123.45.67.89`
- **Username:** `root` atau `ubuntu`
- **Password/SSH Key**

**Login:**
```bash
ssh root@123.45.67.89
# atau
ssh -i your-key.pem ubuntu@123.45.67.89
```

### D. Update System

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git vim nano ufw
```

---

## 🌐 Step 2: Konfigurasi DNS Pointing

📖 **Panduan Lengkap:** Lihat [DNS_SETUP_GUIDE.md](DNS_SETUP_GUIDE.md)

### Quick Steps:

1. **Login ke Provider Domain** (Niagahoster/Rumahweb/dll)

2. **Tambahkan DNS Records:**

| Type | Name/Host | Value | TTL |
|------|-----------|-------|-----|
| A | `@` | `123.45.67.89` | 3600 |
| A | `www` | `123.45.67.89` | 3600 |

*Ganti `123.45.67.89` dengan IP server VPS Anda*

3. **Tunggu Propagasi** (5 menit - 24 jam)

4. **Verify DNS:**
   ```bash
   nslookup e-raport-albarokah.online
   ```

---

## 🔥 Step 3: Setup Firewall

```bash
# Setup UFW (Uncomplicated Firewall)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (IMPORTANT!)
sudo ufw allow 22/tcp

# Allow HTTP & HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

**Output yang benar:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

---

## 🐳 Step 4: Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group (optional)
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker-compose --version
```

**Logout dan login kembali** untuk apply docker group.

---

## 📦 Step 5: Clone & Setup Aplikasi

```bash
# Clone repository
git clone https://github.com/Sandiman184/e-raport.git
cd e-raport

# Copy production environment
cp .env.production .env

# Generate secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Edit file .env:**
```bash
nano .env
```

**Isi dengan:**
```env
FLASK_CONFIG=production
SECRET_KEY=paste-hasil-generate-di-sini-minimal-64-karakter
DATABASE_URL=sqlite:////app/storage/data.sqlite
DOMAIN=e-raport-albarokah.online
EMAIL=admin@e-raport-albarokah.online
```

**Tips Generate Secret Key:**
```bash
# Cara 1: Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Cara 2: OpenSSL
openssl rand -hex 32

# Cara 3: /dev/urandom
head -c 32 /dev/urandom | base64
```

Save: `Ctrl+X`, `Y`, `Enter`

---

## 🚀 Step 6: Deploy Aplikasi

### Option A: Automatic Setup (RECOMMENDED)

```bash
# Make script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

Script akan automatic:
1. ✅ Check Docker installation
2. ✅ Create directories
3. ✅ Build containers
4. ✅ Start application

### Option B: Manual Setup

```bash
# Create required directories
mkdir -p storage/backups certbot/conf certbot/www nginx/conf.d

# Build and start containers
docker-compose up -d --build

# Check status
docker-compose ps
```

**Expected output:**
```
NAME              STATUS              PORTS
raport_app        Up                  
raport_nginx      Up                  0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
raport_certbot    Up
```

---

## 🔍 Step 7: Verify HTTP Access

**Test dari server:**
```bash
curl -I http://localhost
```

**Test from browser:**
```
http://e-raport-albarokah.online
# atau
http://123.45.67.89
```

Anda harus melihat halaman login aplikasi.

**Default Login:**
- Username: `admin`
- Password: `admin123`

⚠️ **JANGAN LUPA UBAH PASSWORD!**

---

## 🔒 Step 8: Setup SSL Certificate

📖 **Panduan Lengkap:** Lihat [SSL_SETUP_GUIDE.md](SSL_SETUP_GUIDE.md)

### Quick SSL Setup:

**Prerequisites:**
- ✅ DNS sudah pointing (cek dengan `nslookup`)
- ✅ Aplikasi sudah running
- ✅ Port 80 & 443 terbuka

**Run SSL Setup:**
```bash
chmod +x setup-ssl.sh
./setup-ssl.sh
```

Script akan:
1. ✅ Verify DNS pointing
2. ✅ Request SSL certificate dari Let's Encrypt
3. ✅ Update Nginx config untuk HTTPS
4. ✅ Restart Nginx
5. ✅ Setup auto-renewal

**Jika berhasil:**
```
✅ SSL Certificate berhasil didapatkan!
✅ Nginx configuration updated!
✅ Nginx restarted!

Aplikasi Anda sekarang dapat diakses melalui:
https://e-raport-albarokah.online
```

---

## ✅ Step 9: Verify HTTPS

### A. Test Redirect
```bash
curl -I http://e-raport-albarokah.online
```
Should return: `301 Moved Permanently` (redirect ke HTTPS)

### B. Test HTTPS
```bash
curl -I https://e-raport-albarokah.online
```
Should return: `200 OK`

### C. Test di Browser
```
https://e-raport-albarokah.online
```

Cek:
- ✅ Gembok hijau/aman di address bar
- ✅ Certificate valid (Let's Encrypt)
- ✅ Halaman login muncul

### D. Test SSL Quality
```
https://www.ssllabs.com/ssltest/analyze.html?d=e-raport-albarokah.online
```
Target: **Grade A** atau **A+**

---

## 🔐 Step 10: Security Hardening

### A. Ubah Password Default

1. Login ke https://e-raport-albarokah.online
2. Username: `admin`, Password: `admin123`
3. Go to **Settings** → **Change Password**
4. Gunakan password yang kuat!

### B. SSH Hardening (Optional)

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config
```

Ubah:
```
PermitRootLogin no
PasswordAuthentication no  # Jika pakai SSH key
Port 2222  # Ubah port SSH (optional)
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

### C. Enable Automatic Security Updates

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 💾 Step 11: Setup Backup Otomatis

### A. Manual Backup

```bash
# Using Makefile
make backup

# Or direct Docker command
docker-compose exec web cp /app/storage/data.sqlite /app/storage/backups/backup-$(date +%Y%m%d).sqlite
```

### B. Automated Backup (Cron)

```bash
# Edit crontab
crontab -e
```

**Tambahkan** (backup setiap hari jam 2 pagi):
```bash
# Daily backup at 2 AM
0 2 * * * cd /root/e-raport && docker-compose exec web cp /app/storage/data.sqlite /app/storage/backups/backup-$(date +\%Y\%m\%d).sqlite

# Weekly cleanup (keep only 30 days)
0 3 * * 0 find /root/e-raport/storage/backups -name "backup-*.sqlite" -mtime +30 -delete
```

### C. Backup ke External Storage (Optional)

**Using rsync to backup server:**
```bash
# Install rclone
curl https://rclone.org/install.sh | sudo bash

# Configure (e.g., Google Drive)
rclone config

# Add to cron
0 4 * * * rclone copy /root/e-raport/storage/backups mybackup:e-raport-backups
```

---

## 📊 Step 12: Monitoring & Maintenance

### A. View Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f certbot
```

### B. Check Container Health

```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# Disk usage
df -h
du -sh storage/
```

### C. Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific
docker-compose restart web
docker-compose restart nginx
```

### D. Update Application

```bash
# Pull latest code
cd /root/e-raport
git pull

# Rebuild and restart
docker-compose up -d --build
```

### E. Monitor SSL Auto-Renewal

```bash
# Check certificate status
docker-compose exec certbot certbot certificates

# Test renewal
docker-compose run --rm certbot renew --dry-run

# View renewal logs
docker-compose logs certbot
```

---

## 🎯 Production Checklist

### Pre-Launch:
- [ ] VPS setup dan accessible via SSH
- [ ] DNS pointing ke IP server
- [ ] Firewall configured (port 22, 80, 443)
- [ ] Docker & Docker Compose installed
- [ ] Repository cloned
- [ ] `.env` configured dengan secret key yang secure

### Deployment:
- [ ] `./setup.sh` berhasil dijalankan
- [ ] Aplikasi accessible via HTTP
- [ ] `./setup-ssl.sh` berhasil dijalankan
- [ ] Aplikasi accessible via HTTPS
- [ ] HTTP auto-redirect ke HTTPS
- [ ] SSL certificate valid (cek di browser)

### Post-Deployment:
- [ ] Password default sudah diubah
- [ ] Backup otomatis sudah disetup
- [ ] Monitoring logs berjalan
- [ ] SSL auto-renewal working
- [ ] Performance test (loading speed)

---

## 🛠️ Useful Commands

```bash
# Application Management
make up              # Start application
make down            # Stop application
make restart         # Restart application
make logs            # View logs
make backup          # Backup database

# Docker Compose
docker-compose ps                # Status
docker-compose logs -f           # Logs
docker-compose restart           # Restart
docker-compose up -d --build     # Rebuild & restart

# SSL Management
./setup-ssl.sh                   # Setup SSL
make renew-ssl                   # Manual renewal
make check-ssl                   # Check cert status

# System
sudo ufw status                  # Firewall status
df -h                            # Disk space
free -h                          # Memory usage
top                              # Process monitor
```

---

## 🆘 Troubleshooting

### Problem: Container tidak start

```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Restart Docker
sudo systemctl restart docker
docker-compose up -d
```

### Problem: DNS tidak resolve

```bash
# Verify DNS
nslookup e-raport-albarokah.online
dig e-raport-albarokah.online

# Flush DNS (di komputer lokal)
# Windows: ipconfig /flushdns
# Linux: sudo systemd-resolve --flush-caches

# Wait for propagation (up to 24 hours)
```

### Problem: SSL gagal

```bash
# Check DNS first!
nslookup e-raport-albarokah.online

# Check ports
sudo ufw status
sudo netstat -tlnp | grep :80

# Check Nginx
docker-compose logs nginx

# Retry SSL setup
./setup-ssl.sh
```

### Problem: Website lambat

```bash
# Check resources
docker stats

# Check disk
df -h

# Optimize database (if large)
docker-compose exec web sqlite3 /app/storage/data.sqlite "VACUUM;"

# Restart application
docker-compose restart
```

---

## 📈 Performance Optimization

### A. Enable Gzip (Already configured di Nginx)

### B. Browser Caching

Already configured di `nginx.conf`

### C. Database Optimization

```bash
# Vacuum database regularly
docker-compose exec web sqlite3 /app/storage/data.sqlite "VACUUM;"
```

### D. Upgrade Server (if needed)

Jika traffic tinggi:
- Upgrade RAM (1GB → 2GB)
- Tambah worker Gunicorn di Dockerfile
- Consider menggunakan PostgreSQL/MySQL

---

## 💰 Estimasi Biaya

**Monthly Cost:**
- VPS (1GB RAM): $5-6/month
- Domain (.online): ~$1/month ($12/year)
- SSL Certificate: **FREE** (Let's Encrypt)

**Total: ~$6-7/month** atau **$80-90/year**

---

## 🎉 Selamat!

Aplikasi E-Raport Anda sekarang **LIVE** di production!

**Access:** https://e-raport-albarokah.online

**Next Steps:**
1. ✅ Setup backup otomatis
2. ✅ Monitor logs secara berkala
3. ✅ Update aplikasi sesuai kebutuhan
4. ✅ Train users untuk menggunakan aplikasi

---

## 📞 Support

Jika ada masalah:
1. Cek dokumentasi lengkap di repository
2. Lihat logs: `docker-compose logs -f`
3. Restart: `docker-compose restart`
4. Buat issue di GitHub

---

**Happy Production! 🚀🎊**
