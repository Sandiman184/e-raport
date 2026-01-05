# 🏗️ Arsitektur Deployment E-Raport

## Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERNET                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTPS (Port 443)
                        │ HTTP  (Port 80)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                     YOUR SERVER                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Docker Compose Network                  │   │
│  │                                                       │   │
│  │  ┌──────────────────────────────────────────┐       │   │
│  │  │         Nginx (Reverse Proxy)             │       │   │
│  │  │  - Port 80 (HTTP → HTTPS redirect)       │       │   │
│  │  │  - Port 443 (HTTPS with SSL)             │       │   │
│  │  │  - Security Headers                       │       │   │
│  │  │  - Static File Serving                    │       │   │
│  │  └──────────┬───────────────────────────────┘       │   │
│  │             │ Proxy Pass                             │   │
│  │             │                                         │   │
│  │  ┌──────────▼───────────────────────────────┐       │   │
│  │  │      Flask Application (Gunicorn)        │       │   │
│  │  │  - Port 8000 (internal)                  │       │   │
│  │  │  - 4 Worker Processes                    │       │   │
│  │  │  - Session Management                    │       │   │
│  │  │  - Business Logic                        │       │   │
│  │  └──────────┬───────────────────────────────┘       │   │
│  │             │                                         │   │
│  │             │ SQLAlchemy ORM                          │   │
│  │             │                                         │   │
│  │  ┌──────────▼───────────────────────────────┐       │   │
│  │  │         SQLite Database                  │       │   │
│  │  │  - File: storage/data.sqlite             │       │   │
│  │  │  - Persistent Volume                     │       │   │
│  │  └──────────────────────────────────────────┘       │   │
│  │                                                       │   │
│  │  ┌──────────────────────────────────────────┐       │   │
│  │  │         Certbot (SSL Manager)            │       │   │
│  │  │  - Auto SSL Certificate Renewal          │       │   │
│  │  │  - Let's Encrypt Integration             │       │   │
│  │  │  - Runs every 12 hours                   │       │   │
│  │  └──────────────────────────────────────────┘       │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │             Persistent Volumes                         │   │
│  │  - ./storage (Database + Uploads)                     │   │
│  │  - ./certbot/conf (SSL Certificates)                  │   │
│  │  - ./certbot/www (ACME Challenges)                    │   │
│  └───────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

## Komponen Utama

### 1. **Nginx (Reverse Proxy)**
- **Image:** `nginx:alpine`
- **Fungsi:**
  - Menerima semua traffic dari internet
  - Redirect HTTP ke HTTPS
  - SSL/TLS termination
  - Reverse proxy ke aplikasi Flask
  - Serve static files (jika ada)
  - Security headers injection
- **Ports:** 80 (HTTP), 443 (HTTPS)

### 2. **Flask Application (Web Service)**
- **Image:** Custom (built from Dockerfile)
- **Base:** Python 3.11-slim
- **Server:** Gunicorn (4 workers)
- **Fungsi:**
  - Handle semua business logic
  - Render HTML templates
  - API endpoints
  - Session management
  - Database operations
- **Port:** 8000 (internal only)

### 3. **SQLite Database**
- **Type:** File-based database
- **Location:** `./storage/data.sqlite`
- **Features:**
  - Persistent storage via volume mount
  - Auto-created on first run
  - Backup-friendly (single file)
- **Suitable for:** Small to medium scale (< 1000 concurrent users)

### 4. **Certbot (SSL Manager)**
- **Image:** `certbot/certbot`
- **Fungsi:**
  - Generate SSL certificates from Let's Encrypt
  - Auto-renewal every 60 days
  - Runs health check every 12 hours
- **Free:** 90-day certificates, auto-renewed

## Data Flow

### User Request Flow (HTTPS)
```
User Browser
    │
    │ 1. HTTPS Request (443)
    ▼
Nginx (SSL Termination)
    │
    │ 2. Decrypt & proxy to Flask
    ▼
Flask/Gunicorn (Port 8000)
    │
    │ 3. Process request
    │ 4. Query database if needed
    ▼
SQLite Database
    │
    │ 5. Return data
    ▼
Flask generates HTML
    │
    │ 6. Response
    ▼
Nginx (Add security headers)
    │
    │ 7. Encrypt & send
    ▼
User Browser (Render page)
```

### SSL Certificate Flow
```
Certbot
    │
    │ 1. Request certificate
    ▼
Let's Encrypt
    │
    │ 2. ACME Challenge (HTTP-01)
    ▼
Nginx serves /.well-known/acme-challenge/
    │
    │ 3. Validation successful
    ▼
Certbot receives certificate
    │
    │ 4. Save to /etc/letsencrypt/
    ▼
Nginx reloads config (uses new cert)
```

## Resource Requirements

### Minimum (Development/Testing)
- **CPU:** 1 core
- **RAM:** 512 MB
- **Storage:** 5 GB
- **Users:** < 50 concurrent

### Recommended (Production)
- **CPU:** 2 cores
- **RAM:** 2 GB
- **Storage:** 20 GB
- **Users:** < 500 concurrent

### Scaling Options
Jika butuh scale lebih besar:
1. **Database:** Ganti SQLite dengan PostgreSQL/MySQL
2. **Application:** Tambah worker Gunicorn atau scale horizontal
3. **Load Balancer:** Tambahkan jika perlu multiple app instances
4. **Caching:** Redis untuk session & caching

## Security Features

### Network Security
- ✅ HTTPS only (HTTP auto-redirect)
- ✅ TLS 1.2+ encryption
- ✅ Strong cipher suites
- ✅ Internal network isolation (Docker)

### Application Security
- ✅ CSRF protection (Flask-WTF)
- ✅ Secure session cookies
- ✅ Password hashing (Werkzeug)
- ✅ SQL injection protection (SQLAlchemy)

### HTTP Security Headers
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

## Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f certbot
```

### Log Locations
- **Nginx Access:** `/var/log/nginx/access.log` (inside container)
- **Nginx Error:** `/var/log/nginx/error.log`
- **Flask Output:** Container stdout (via docker-compose logs)

### Health Checks
```bash
# Container status
docker-compose ps

# Nginx config test
docker-compose exec nginx nginx -t

# SSL certificate expiry
docker-compose exec certbot certbot certificates
```

## Backup Strategy

### Database Backup
```bash
# Manual backup
docker-compose exec web cp /app/storage/data.sqlite \
    /app/storage/backup-$(date +%Y%m%d-%H%M%S).sqlite

# Automated backup (add to cron)
0 2 * * * cd /path/to/app && docker-compose exec web \
    cp /app/storage/data.sqlite /app/storage/backup-$(date +%Y%m%d).sqlite
```

### Full Backup
```bash
# Backup everything
tar -czf backup-$(date +%Y%m%d).tar.gz \
    storage/ \
    certbot/conf/ \
    .env
```

### Restore
```bash
# Extract backup
tar -xzf backup-20260105.tar.gz

# Restart services
docker-compose restart
```

## Update & Maintenance

### Update Application Code
```bash
git pull
docker-compose up -d --build
```

### Update Docker Images
```bash
docker-compose pull
docker-compose up -d
```

### Update SSL Certificate (Manual)
```bash
docker-compose run --rm certbot renew
docker-compose restart nginx
```

## Cost Estimation

### Hosting Options
1. **DigitalOcean Droplet:** $6/month (1GB RAM)
2. **Vultr VPS:** $6/month (1GB RAM)
3. **AWS Lightsail:** $5/month (1GB RAM)
4. **Linode:** $5/month (1GB RAM)

### Additional Costs
- **Domain:** $10-15/year
- **SSL Certificate:** FREE (Let's Encrypt)
- **Backup Storage:** Optional

**Total:** ~$80-100/year untuk aplikasi production-ready dengan HTTPS!

## Next Steps

1. ✅ Setup server dengan Docker
2. ✅ Deploy aplikasi (`docker-compose up -d`)
3. ✅ Setup SSL (`./setup-ssl.sh`)
4. ✅ Configure backups (cron job)
5. ✅ Monitor logs regularly
6. ✅ Update aplikasi as needed

---

**Catatan:** Arsitektur ini sudah production-ready untuk skala kecil hingga menengah. Untuk skala lebih besar, pertimbangkan menggunakan PostgreSQL, Redis, dan load balancer.
