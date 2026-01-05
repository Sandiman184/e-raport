# 🌐 E-Raport Albarokah - Production Configuration

## Domain Information

**Primary Domain:** e-raport-albarokah.online  
**WWW Domain:** www.e-raport-albarokah.online  
**Admin Email:** admin@e-raport-albarokah.online

---

## 🚀 Quick Deploy

### One-Command Deployment:

```bash
# Clone repository
git clone https://github.com/Sandiman184/e-raport.git
cd e-raport

# Run automated deployment
chmod +x deploy-production.sh
./deploy-production.sh
```

Script akan otomatis:
- ✅ Install Docker (jika belum ada)
- ✅ Check DNS pointing
- ✅ Setup environment dengan domain yang benar
- ✅ Build dan start containers
- ✅ Setup SSL certificate (jika DNS sudah ready)

---

## 📋 DNS Configuration

### Required DNS Records:

Login ke provider domain Anda dan tambahkan:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_SERVER_IP | 3600 |
| A | www | YOUR_SERVER_IP | 3600 |

**Contoh:**
```
Type: A
Host: @
Points To: 123.45.67.89  (ganti dengan IP server Anda)
TTL: 3600

Type: A
Host: www
Points To: 123.45.67.89
TTL: 3600
```

### Verify DNS:

```bash
nslookup e-raport-albarokah.online
```

---

## 🔒 SSL Certificate

### Automatic Setup:

Setelah DNS pointing:

```bash
./setup-ssl.sh
```

### Manual Setup:

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

---

## 📖 Documentation

Detailed guides available:

1. **[PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)**
   - Complete production deployment guide
   - VPS setup
   - Security configuration

2. **[DNS_SETUP_GUIDE.md](DNS_SETUP_GUIDE.md)**
   - DNS pointing step-by-step
   - Provider-specific instructions
   - Troubleshooting DNS issues

3. **[SSL_SETUP_GUIDE.md](SSL_SETUP_GUIDE.md)**
   - SSL certificate setup
   - Let's Encrypt configuration
   - Auto-renewal setup

4. **[DEPLOYMENT.md](DEPLOYMENT.md)**
   - General deployment guide
   - Docker configuration
   - Nginx setup

---

## 🎯 Access Information

### Production URL:
```
https://e-raport-albarokah.online
```

### Default Login:
```
Username: admin
Password: admin123
```

⚠️ **CRITICAL:** Change password immediately after first login!

---

## 🔧 Server Requirements

### Minimum:
- **OS:** Ubuntu 22.04 LTS
- **RAM:** 1GB
- **CPU:** 1 Core
- **Storage:** 10GB
- **Ports:** 22, 80, 443

### Recommended:
- **RAM:** 2GB
- **CPU:** 2 Cores
- **Storage:** 20GB

---

## 💾 Backup

### Manual Backup:
```bash
make backup
```

### Automated Backup (Cron):
```bash
crontab -e
```

Add:
```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/e-raport && make backup
```

---

## 📊 Monitoring

### View Logs:
```bash
docker-compose logs -f
```

### Container Status:
```bash
docker-compose ps
```

### Resource Usage:
```bash
docker stats
```

---

## 🆘 Emergency Contacts

### DNS Provider:
- Check your domain provider dashboard
- Support: [Your DNS Provider Support]

### SSL Issues:
- Let's Encrypt Status: https://letsencrypt.status.io/
- Rate Limits: 5 certificates/week per domain

### Server Issues:
- Check VPS provider dashboard
- Restart: `docker-compose restart`

---

## 📞 Support

For issues or questions:
1. Check documentation first
2. View logs: `docker-compose logs -f`
3. Create issue on GitHub

---

**Production Deployment for e-raport-albarokah.online** 🚀

Last Updated: 2026-01-05
