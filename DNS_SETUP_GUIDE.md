# 🌐 Panduan DNS Pointing untuk e-raport-albarokah.online

Panduan lengkap untuk konfigurasi DNS agar domain **e-raport-albarokah.online** pointing ke server VPS Anda.

---

## 📋 Yang Anda Butuhkan

1. **Domain:** e-raport-albarokah.online (sudah Anda miliki)
2. **Server VPS** dengan:
   - IP Address Public (contoh: `123.45.67.89`)
   - Port 80 dan 443 terbuka
   - Docker sudah terinstall

---

## 🔍 Step 1: Cek IP Address Server Anda

Setelah beli/setup VPS, dapatkan IP address public server:

### Di Server (SSH ke VPS):
```bash
# Cek IP public
curl ifconfig.me
# atau
curl ipinfo.io/ip
# atau  
hostname -I
```

**Contoh output:** `123.45.67.89`

📝 **Catat IP ini!** Anda akan menggunakannya untuk DNS configuration.

---

## 🌍 Step 2: Konfigurasi DNS di Provider Domain

Login ke website tempat Anda beli domain (provider DNS). Biasanya provider domain Indonesia:
- **Niagahoster**
- **Rumahweb**
- **Hostinger**
- **Cloudflare** (jika domain sudah di-transfer)
- **GoDaddy**
- **Namecheap**
- dll.

### A. Login ke Control Panel Domain

1. Login ke akun provider domain Anda
2. Cari menu **"DNS Management"** atau **"DNS Settings"** atau **"Domain Settings"**
3. Pilih domain: **e-raport-albarokah.online**

### B. Tambahkan DNS Records

Anda perlu menambahkan **A Record** yang mengarahkan domain ke IP server.

#### 🎯 DNS Records yang Harus Ditambahkan:

| Type | Name/Host | Value/Points To | TTL |
|------|-----------|-----------------|-----|
| **A** | `@` | `123.45.67.89` | 3600 |
| **A** | `www` | `123.45.67.89` | 3600 |

**Keterangan:**
- **Type:** A (Address Record)
- **Name/Host:** 
  - `@` = root domain (e-raport-albarokah.online)
  - `www` = subdomain www (www.e-raport-albarokah.online)
- **Value:** IP address server VPS Anda
- **TTL:** 3600 (1 jam) atau biarkan default

#### 📸 Contoh Konfigurasi DNS:

**Niagahoster/Rumahweb:**
```
Type: A
Host: @
Points To: 123.45.67.89
TTL: 3600
```

**Cloudflare:**
```
Type: A
Name: @
IPv4 Address: 123.45.67.89
Proxy Status: DNS only (Gray cloud)
TTL: Auto
```

### C. Hapus Record Lama (Jika Ada)

Jika ada record lama yang mengarah ke tempat lain, **hapus** atau **edit** agar mengarah ke IP server baru Anda.

### D. Simpan Perubahan

Klik **Save** atau **Update** untuk menyimpan perubahan DNS.

---

## ⏱️ Step 3: Tunggu Propagasi DNS

Setelah update DNS, perlu waktu untuk propagasi (penyebaran):

- **Minimal:** 5-15 menit
- **Maksimal:** 24-48 jam (jarang)
- **Rata-rata:** 1-4 jam

### Cek Status Propagasi DNS:

#### A. Menggunakan Online Tools:

**Website untuk cek DNS:**
1. https://dnschecker.org
   - Masukkan: `e-raport-albarokah.online`
   - Pilih type: `A`
   - Cek apakah IP sudah benar di berbagai lokasi

2. https://www.whatsmydns.net
   - Masukkan: `e-raport-albarokah.online`
   - Type: `A`

#### B. Menggunakan Command Line:

**Windows (PowerShell):**
```powershell
nslookup e-raport-albarokah.online
```

**Linux/Mac:**
```bash
# Menggunakan nslookup
nslookup e-raport-albarokah.online

# Menggunakan dig (lebih detail)
dig e-raport-albarokah.online

# Atau host
host e-raport-albarokah.online
```

**Output yang benar:**
```
Name:    e-raport-albarokah.online
Address: 123.45.67.89
```

Jika IP sudah muncul dan sesuai dengan IP server Anda, berarti **DNS sudah pointing!** ✅

---

## 🚀 Step 4: Deploy Aplikasi di Server

Setelah DNS pointing berhasil, deploy aplikasi:

### A. SSH ke Server VPS

```bash
ssh root@123.45.67.89
# atau
ssh username@e-raport-albarokah.online
```

### B. Clone Repository

```bash
# Install git jika belum ada
apt update && apt install git -y

# Clone aplikasi
git clone https://github.com/Sandiman184/e-raport.git
cd e-raport
```

### C. Setup Environment

```bash
# Copy production config
cp .env.production .env

# Generate secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Edit .env dan paste secret key
nano .env
```

**Edit file .env:**
```env
FLASK_CONFIG=production
SECRET_KEY=<paste-hasil-generate-secret-key-di-sini>
DATABASE_URL=sqlite:////app/storage/data.sqlite
DOMAIN=e-raport-albarokah.online
EMAIL=admin@e-raport-albarokah.online
```

Save: `Ctrl+X`, `Y`, `Enter`

### D. Jalankan Setup

```bash
# Make scripts executable
chmod +x setup.sh setup-ssl.sh

# Run setup
./setup.sh
```

Script akan:
- ✅ Install Docker (jika belum ada)
- ✅ Setup environment
- ✅ Build containers
- ✅ Start aplikasi

---

## 🔒 Step 5: Setup SSL Certificate

Setelah aplikasi running dan DNS sudah pointing, setup SSL:

```bash
# Pastikan DNS sudah pointing (cek dulu!)
nslookup e-raport-albarokah.online

# Jika IP sudah benar, jalankan SSL setup
./setup-ssl.sh
```

Script akan:
1. ✅ Request SSL certificate dari Let's Encrypt
2. ✅ Configure Nginx untuk HTTPS
3. ✅ Auto-redirect HTTP ke HTTPS
4. ✅ Setup auto-renewal (setiap 60 hari)

---

## ✅ Step 6: Verifikasi Setup

### A. Test HTTP (akan auto-redirect ke HTTPS)
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

Buka browser dan akses:
```
https://e-raport-albarokah.online
```

Anda harus melihat:
- ✅ Halaman login aplikasi
- ✅ Gembok hijau/aman di address bar
- ✅ Certificate valid dari Let's Encrypt

### D. Login

**Default credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Segera ubah password setelah login pertama!**

---

## 🔧 Troubleshooting

### ❌ Problem: DNS tidak resolve

**Cek:**
```bash
nslookup e-raport-albarokah.online
```

**Solusi:**
- Tunggu lebih lama (propagasi bisa sampai 24 jam)
- Cek DNS settings di provider domain
- Pastikan menggunakan `@` untuk root domain
- Clear DNS cache di komputer Anda:
  ```bash
  # Windows
  ipconfig /flushdns
  
  # Linux
  sudo systemd-resolve --flush-caches
  
  # Mac
  sudo dscacheutil -flushcache
  ```

### ❌ Problem: SSL Certificate gagal

**Cek:**
```bash
docker-compose logs certbot
```

**Solusi:**
1. **Pastikan DNS sudah pointing** (ini yang paling sering!)
   ```bash
   nslookup e-raport-albarokah.online
   ```

2. **Pastikan port 80 & 443 terbuka:**
   ```bash
   # Cek firewall
   sudo ufw status
   
   # Buka port jika perlu
   sudo ufw allow 80
   sudo ufw allow 443
   ```

3. **Pastikan Nginx running:**
   ```bash
   docker-compose ps
   ```

4. **Test manual (dry-run):**
   ```bash
   docker-compose run --rm certbot certonly --dry-run \
       --webroot --webroot-path=/var/www/certbot \
       -d e-raport-albarokah.online \
       -d www.e-raport-albarokah.online
   ```

### ❌ Problem: "Port 80 already in use"

**Solusi:**
```bash
# Cek apa yang pakai port 80
sudo netstat -tlnp | grep :80

# Stop service yang konflik (contoh: apache2)
sudo systemctl stop apache2
sudo systemctl disable apache2

# Restart docker
docker-compose restart
```

### ❌ Problem: Website tidak bisa diakses

**Cek logs:**
```bash
docker-compose logs -f
```

**Cek container status:**
```bash
docker-compose ps
```

**Restart semua:**
```bash
docker-compose restart
```

---

## 📊 Summary Setup

### Checklist Lengkap:

- [ ] **Step 1:** Dapatkan IP address server VPS
- [ ] **Step 2:** Konfigurasi DNS A Record di provider domain
  - [ ] A Record: `@` → IP Server
  - [ ] A Record: `www` → IP Server
- [ ] **Step 3:** Tunggu & verify DNS propagasi (nslookup)
- [ ] **Step 4:** Deploy aplikasi di server
  - [ ] Clone repository
  - [ ] Setup .env dengan domain yang benar
  - [ ] Jalankan `./setup.sh`
- [ ] **Step 5:** Setup SSL certificate
  - [ ] Pastikan DNS pointing
  - [ ] Jalankan `./setup-ssl.sh`
- [ ] **Step 6:** Verifikasi setup
  - [ ] Test HTTP (auto-redirect)
  - [ ] Test HTTPS (SSL valid)
  - [ ] Login & ubah password default

---

## 🎯 Domain Configuration Summary

**Domain:** e-raport-albarokah.online  
**DNS Records:**
```
Type: A
Host: @
Value: [IP_SERVER_ANDA]

Type: A  
Host: www
Value: [IP_SERVER_ANDA]
```

**SSL Certificate:** Let's Encrypt (Free, Auto-renewal)  
**Access:** https://e-raport-albarokah.online

---

## 📞 Bantuan Lebih Lanjut

Jika masih ada masalah:

1. **Cek DNS:** https://dnschecker.org
2. **Test SSL:** https://www.ssllabs.com/ssltest/
3. **Cek Logs:** `docker-compose logs -f`
4. **Restart:** `docker-compose restart`

---

**Selamat! Domain e-raport-albarokah.online Anda siap dengan HTTPS!** 🎉🔒
