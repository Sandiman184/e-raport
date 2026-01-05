#!/bin/bash

# Script untuk setup SSL dengan Let's Encrypt
# Jalankan script ini setelah docker-compose up dan domain sudah pointing

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup SSL Certificate dengan Certbot${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Detect Docker Compose command
echo "Detecting Docker Compose..."
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo -e "${GREEN}✓ Using: docker-compose${NC}"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo -e "${GREEN}✓ Using: docker compose (plugin)${NC}"
else
    echo -e "${RED}✗ Docker Compose not found!${NC}"
    echo -e "${YELLOW}Please install Docker Compose first.${NC}"
    echo ""
    echo "Run: ./fix-docker-compose.sh"
    exit 1
fi
echo ""

# Baca domain dari .env atau input manual
if [ -f .env ]; then
    source .env
fi

if [ -z "$DOMAIN" ]; then
    echo -e "${YELLOW}Domain tidak ditemukan di .env${NC}"
    read -p "Masukkan domain Anda (contoh: raport.sekolah.id): " DOMAIN
fi

if [ -z "$EMAIL" ]; then
    echo -e "${YELLOW}Email tidak ditemukan di .env${NC}"
    read -p "Masukkan email untuk notifikasi SSL: " EMAIL
fi

echo ""
echo -e "${GREEN}Domain: ${NC}$DOMAIN"
echo -e "${GREEN}Email: ${NC}$EMAIL"
echo ""

read -p "Lanjutkan? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo -e "${RED}Dibatalkan${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 1: Mendapatkan SSL Certificate...${NC}"

# Request certificate with proper entrypoint override
$DOCKER_COMPOSE_CMD run --rm --entrypoint certbot certbot \
    certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ SSL Certificate berhasil didapatkan!${NC}"
    echo ""
    
    echo -e "${YELLOW}Step 2: Update Nginx configuration...${NC}"
    
    # Replace template dengan domain aktual
    sed "s/\${DOMAIN}/$DOMAIN/g" nginx/conf.d/app.conf.template > nginx/conf.d/app.conf
    
    echo -e "${GREEN}✓ Nginx configuration updated!${NC}"
    echo ""
    
    echo -e "${YELLOW}Step 3: Restart Nginx...${NC}"
    $DOCKER_COMPOSE_CMD restart nginx
    
    echo -e "${GREEN}✓ Nginx restarted!${NC}"
    echo ""
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  SSL Setup Selesai!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${GREEN}Aplikasi Anda sekarang dapat diakses melalui:${NC}"
    echo -e "${GREEN}https://$DOMAIN${NC}"
    echo -e "${GREEN}https://www.$DOMAIN${NC}"
    echo ""
    echo -e "${YELLOW}Catatan: Certificate akan di-renew otomatis oleh Certbot${NC}"
    
else
    echo -e "${RED}✗ Gagal mendapatkan SSL Certificate${NC}"
    echo ""
    echo -e "${YELLOW}Pastikan:${NC}"
    echo "1. Domain sudah pointing ke IP server ini"
    echo "2. Port 80 dan 443 terbuka"
    echo "3. Docker containers sudah running ($DOCKER_COMPOSE_CMD ps)"
    exit 1
fi
