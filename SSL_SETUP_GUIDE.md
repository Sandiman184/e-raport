# 🔒 Panduan Setup SSL Certificate untuk e-raport-albarokah.online

Panduan lengkap setup SSL/HTTPS menggunakan Certbot dan Let's Encrypt untuk domain **e-raport-albarokah.online**.

---

## 🎯 Apa yang Akan Kita Capai?

Setelah mengikuti panduan ini, website Anda akan:
- ✅ Diakses dengan HTTPS (gembok hijau di browser)
- ✅ SSL Certificate valid dari Let's Encrypt (GRATIS!)
- ✅ Auto-redirect dari HTTP ke HTTPS
- ✅ Auto-renewal certificate setiap 60 hari
- ✅ Security headers untuk keamanan maksimal

---

## 📋 Prerequisites

Sebelum setup SSL, pastikan:

### ✅ Checklist Pre-SSL:

1. **DNS Sudah Pointing** ⭐ (PALING PENTING!)
   ```bash
   nslookup e-raport-albarokah.online
   ```
   Output harus menunjukkan IP server Anda.

2. **Aplikasi Sudah Running**
   ```bash
   docker-compose ps
   ```
   Semua container harus status "Up".

3. **Port 80 & 443 Terbuka**
   ```bash
   sudo ufw status
   ```
   Port 80 dan 443 harus allow.

4. **Email Valid untuk Notifikasi**
   - Gunakan: `admin@e-raport-albarokah.online`
   - Atau email Gmail/lainnya yang valid

---

## 🚀 Metode 1: Automatic Setup (RECOMMENDED)

### Paling Mudah - Satu Klik!

```bash
# Pastikan di direktori aplikasi
cd /path/to/e-raport

# Jalankan script SSL
chmod +x setup-ssl.sh
./setup-ssl.sh
```

Script akan:
1. ✅ Verify DNS pointing
2. ✅ Request SSL certificate dari Let's Encrypt
3. ✅ Update Nginx config untuk HTTPS
4. ✅ Restart Nginx
5. ✅ Test HTTPS

**Jika berhasil**, Anda akan melihat:
```
✅ SSL Certificate berhasil didapatkan!
✅ Nginx configuration updated!
✅ Nginx restarted!

Aplikasi Anda sekarang dapat diakses melalui:
https://e-raport-albarokah.online
```

**Selesai!** Loncat ke section [Verifikasi Setup](#verifikasi-setup).

---

## 🔧 Metode 2: Manual Setup (Advanced)

Jika ingin setup manual atau automatic script gagal:

### Step 1: Verify Prerequisites

```bash
# 1. Cek DNS
nslookup e-raport-albarokah.online

# 2. Cek containers
docker-compose ps

# 3. Cek firewall
sudo ufw status
```

### Step 2: Request SSL Certificate

```bash
# Dry run dulu (test tanpa benar-benar request)
docker-compose run --rm certbot certonly --dry-run \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@e-raport-albarokah.online \
    --agree-tos \
    --no-eff-email \
    -d e-raport-albarokah.online \
    -d www.e-raport-albarokah.online
```

**Jika dry-run berhasil**, request certificate asli:

```bash
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@e-raport-albarokah.online \
    --agree-tos \
    --no-eff-email \
    -d e-raport-albarokah.online \
    -d www.e-raport-albarokah.online
```

**Output yang benar:**
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/e-raport-albarokah.online/fullchain.pem
Key is saved at: /etc/letsencrypt/live/e-raport-albarokah.online/privkey.pem
```

### Step 3: Update Nginx Configuration

Buat file config untuk HTTPS:

```bash
nano nginx/conf.d/app.conf
```

**Paste konfigurasi berikut:**

```nginx
# HTTP - Redirect ke HTTPS
server {
    listen 80;
    server_name e-raport-albarokah.online www.e-raport-albarokah.online;
    
    # Certbot challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect semua ke HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - Main Server
server {
    listen 443 ssl http2;
    server_name e-raport-albarokah.online www.e-raport-albarokah.online;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/e-raport-albarokah.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/e-raport-albarokah.online/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client body size
    client_max_body_size 16M;

    # Proxy to Flask application
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Certbot challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 4: Test & Restart Nginx

```bash
# Test konfigurasi Nginx
docker-compose exec nginx nginx -t

# Jika OK, restart Nginx
docker-compose restart nginx
```

---

## ✅ Verifikasi Setup

### 1. Test HTTP Redirect

```bash
curl -I http://e-raport-albarokah.online
```

**Expected output:**
```
HTTP/1.1 301 Moved Permanently
Location: https://e-raport-albarokah.online/
```

### 2. Test HTTPS

```bash
curl -I https://e-raport-albarokah.online
```

**Expected output:**
```
HTTP/2 200
```

### 3. Test di Browser

Buka: **https://e-raport-albarokah.online**

Cek:
- ✅ Gembok hijau/aman di address bar
- ✅ Certificate valid (klik gembok → Certificate)
- ✅ Issued by: Let's Encrypt
- ✅ Valid for: e-raport-albarokah.online

### 4. Test SSL Quality

Gunakan SSL Labs:
```
https://www.ssllabs.com/ssltest/analyze.html?d=e-raport-albarokah.online
```

Target: **Grade A** atau **A+**

---

## 🔄 Auto-Renewal Certificate

Certificate Let's Encrypt valid **90 hari**. Aplikasi sudah di-setup untuk auto-renewal.

### Cara Kerja Auto-Renewal:

Certbot container akan:
- ✅ Cek certificate setiap 12 jam
- ✅ Renew jika kurang dari 30 hari expired
- ✅ Reload Nginx setelah renewal

**Tidak perlu action manual!** 🎉

### Manual Renewal (jika perlu):

```bash
# Test renewal (dry-run)
docker-compose run --rm certbot renew --dry-run

# Force renewal
docker-compose run --rm certbot renew

# Restart nginx setelah renewal
docker-compose restart nginx
```

### Cek Status Certificate:

```bash
# Lihat info certificate
docker-compose exec certbot certbot certificates

# Output:
# Certificate Name: e-raport-albarokah.online
# Expiry Date: 2026-04-05 (VALID: 89 days)
```

### Setup Monitoring (Optional):

Tambah cron job untuk log renewal:

```bash
crontab -e
```

Tambahkan:
```bash
0 0 * * * docker-compose -f /path/to/e-raport/docker-compose.yml exec certbot certbot renew >> /var/log/certbot-renewal.log 2>&1
```

---

## 🛠️ Troubleshooting SSL

### ❌ Problem: "Failed to obtain certificate"

**Kemungkinan penyebab:**

#### 1. DNS Belum Pointing
```bash
# Cek DNS
nslookup e-raport-albarokah.online
dig e-raport-albarokah.online
```

**Solusi:** Tunggu propagasi DNS (bisa sampai 24 jam)

#### 2. Port 80 Tidak Terbuka
```bash
# Cek firewall
sudo ufw status

# Buka port
sudo ufw allow 80
sudo ufw allow 443
```

#### 3. Nginx Tidak Running
```bash
# Cek status
docker-compose ps

# Restart
docker-compose restart nginx
```

#### 4. Webroot Path Salah
```bash
# Cek volume mount di docker-compose.yml
# Harus ada: ./certbot/www:/var/www/certbot
```

### ❌ Problem: "Certificate already exists"

Jika mau request ulang:

```bash
# Delete certificate lama
docker-compose run --rm certbot delete --cert-name e-raport-albarokah.online

# Request baru
./setup-ssl.sh
```

### ❌ Problem: "Too many requests"

Let's Encrypt punya rate limit:
- **5 certificates/week** untuk domain yang sama

**Solusi:**
- Tunggu 1 minggu
- Atau gunakan staging server untuk testing:
  ```bash
  docker-compose run --rm certbot certonly --staging \
      --webroot --webroot-path=/var/www/certbot \
      -d e-raport-albarokah.online
  ```

### ❌ Problem: Mixed Content Warning

Jika ada warning "mixed content" di browser:

**Penyebab:** Ada resource (CSS/JS/images) yang di-load via HTTP

**Solusi:**
1. Cek di browser console (F12)
2. Update URL resource dari `http://` ke `https://`
3. Atau gunakan protocol-relative URLs: `//example.com/style.css`

### ❌ Problem: Certificate Tidak Auto-Renew

```bash
# Cek certbot container
docker-compose ps certbot

# Lihat logs
docker-compose logs certbot

# Manual test renewal
docker-compose run --rm certbot renew --dry-run
```

---

## 📊 SSL Configuration Summary

**Domain:** e-raport-albarokah.online  
**SSL Provider:** Let's Encrypt (Free)  
**Certificate Type:** Domain Validation (DV)  
**Validity:** 90 days (auto-renewal every 60 days)  
**Encryption:** TLS 1.2 & TLS 1.3  
**Auto-Renewal:** Yes ✅  

**Certificate Locations:**
```
Certificate: /etc/letsencrypt/live/e-raport-albarokah.online/fullchain.pem
Private Key: /etc/letsencrypt/live/e-raport-albarokah.online/privkey.pem
Chain: /etc/letsencrypt/live/e-raport-albarokah.online/chain.pem
```

---

## 🎯 Next Steps

Setelah SSL setup:

1. ✅ **Ubah Password Default**
   - Login: https://e-raport-albarokah.online
   - Username: `admin`
   - Password: `admin123`
   - Segera ubah!

2. ✅ **Setup Backup Otomatis**
   ```bash
   crontab -e
   # Add: 0 2 * * * cd /path/to/e-raport && make backup
   ```

3. ✅ **Monitor Logs**
   ```bash
   docker-compose logs -f
   ```

4. ✅ **Test Performance**
   - https://gtmetrix.com
   - https://pagespeed.web.dev

---

## 📞 Butuh Bantuan?

- **Test SSL:** https://www.ssllabs.com/ssltest/
- **Check DNS:** https://dnschecker.org
- **View Logs:** `docker-compose logs -f certbot`
- **Restart All:** `docker-compose restart`

---

**Selamat! Domain e-raport-albarokah.online sekarang aman dengan SSL/HTTPS!** 🔒🎉
