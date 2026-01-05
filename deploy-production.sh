#!/bin/bash

# Quick Deployment Script for e-raport-albarokah.online
# This script automates the entire deployment process

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

clear

echo -e "${PURPLE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀  E-RAPORT ALBAROKAH PRODUCTION DEPLOYMENT  🚀       ║
║                                                           ║
║             e-raport-albarokah.online                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${GREEN}Automated deployment untuk e-raport-albarokah.online${NC}"
echo ""

# Configuration
DOMAIN="e-raport-albarokah.online"
WWW_DOMAIN="www.e-raport-albarokah.online"
EMAIL="admin@e-raport-albarokah.online"

# Step 1: Check if we're on server
echo -e "${BLUE}[1/8]${NC} Checking environment..."
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}✗ This script must run on Linux server${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Running on Linux${NC}"

# Step 2: Check Docker
echo -e "${BLUE}[2/8]${NC} Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# Check Docker Compose
echo -e "${BLUE}[2.5/8]${NC} Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ docker-compose found${NC}"
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    echo -e "${GREEN}✓ docker compose plugin found${NC}"
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo -e "${YELLOW}Docker Compose not found. Installing...${NC}"
    
    # Try adding Docker repository and install plugin
    echo -e "${YELLOW}Attempting to add Docker repository...${NC}"
    
    # Add Docker's official GPG key
    sudo apt-get update
    sudo apt-get install ca-certificates curl gnupg -y
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes 2>/dev/null
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update and try installing plugin
    sudo apt-get update
    if sudo apt-get install docker-compose-plugin -y 2>/dev/null; then
        echo -e "${GREEN}✓ Docker Compose plugin installed${NC}"
        DOCKER_COMPOSE_CMD="docker compose"
    else
        # Fallback to standalone binary
        echo -e "${YELLOW}Plugin installation failed. Installing standalone Docker Compose...${NC}"
        sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        # Verify installation
        if /usr/local/bin/docker-compose --version &> /dev/null; then
            echo -e "${GREEN}✓ Standalone Docker Compose installed${NC}"
            DOCKER_COMPOSE_CMD="/usr/local/bin/docker-compose"
        else
            echo -e "${RED}✗ Failed to install Docker Compose${NC}"
            echo -e "${YELLOW}Please install manually and run this script again${NC}"
            exit 1
        fi
    fi
fi

# Step 3: Check DNS
echo -e "${BLUE}[3/8]${NC} Checking DNS pointing..."
DNS_IP=$(dig +short $DOMAIN | head -n1)
SERVER_IP=$(curl -s ifconfig.me)

echo -e "  Domain: ${CYAN}$DOMAIN${NC}"
echo -e "  DNS IP: ${CYAN}$DNS_IP${NC}"
echo -e "  Server IP: ${CYAN}$SERVER_IP${NC}"

if [ "$DNS_IP" != "$SERVER_IP" ]; then
    echo -e "${YELLOW}⚠ WARNING: DNS belum pointing ke server ini!${NC}"
    echo -e "${YELLOW}  Anda bisa lanjut deploy, tapi SSL setup akan gagal.${NC}"
    echo -e "${YELLOW}  Setup DNS dulu di provider domain Anda:${NC}"
    echo -e "  ${CYAN}A Record: @ → $SERVER_IP${NC}"
    echo -e "  ${CYAN}A Record: www → $SERVER_IP${NC}"
    echo ""
    read -p "Lanjutkan deployment tanpa SSL? (y/n): " continue
    if [ "$continue" != "y" ]; then
        echo -e "${RED}Deployment dibatalkan${NC}"
        exit 1
    fi
    SKIP_SSL=true
else
    echo -e "${GREEN}✓ DNS sudah pointing ke server ini${NC}"
    SKIP_SSL=false
fi

# Step 4: Setup environment
echo -e "${BLUE}[4/8]${NC} Setting up environment..."

# Generate secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)

# Create .env
cat > .env << EOL
# Production Configuration for e-raport-albarokah.online
FLASK_CONFIG=production
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=sqlite:////app/storage/data.sqlite
DOMAIN=${DOMAIN}
EMAIL=${EMAIL}
EOL

echo -e "${GREEN}✓ Environment configured${NC}"

# Step 5: Create directories
echo -e "${BLUE}[5/8]${NC} Creating directories..."
mkdir -p storage/backups
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p nginx/conf.d

echo -e "${GREEN}✓ Directories created${NC}"

# Step 6: Build and start
echo -e "${BLUE}[6/8]${NC} Building and starting containers..."
echo -e "${YELLOW}This may take a few minutes...${NC}"

$DOCKER_COMPOSE_CMD up -d --build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Containers started${NC}"
else
    echo -e "${RED}✗ Failed to start containers${NC}"
    exit 1
fi

# Wait for services
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Step 7: Check status
echo -e "${BLUE}[7/8]${NC} Checking services..."
$DOCKER_COMPOSE_CMD ps
echo ""

# Step 8: SSL Setup
if [ "$SKIP_SSL" = false ]; then
    echo -e "${BLUE}[8/8]${NC} Setting up SSL certificate..."
    
    # Make setup-ssl.sh executable
    chmod +x setup-ssl.sh
    
    # Run SSL setup with auto-confirm
    echo "y" | ./setup-ssl.sh
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ SSL certificate installed${NC}"
        PROTOCOL="https"
    else
        echo -e "${YELLOW}⚠ SSL setup failed. Using HTTP for now.${NC}"
        PROTOCOL="http"
    fi
else
    echo -e "${BLUE}[8/8]${NC} Skipping SSL setup (DNS not ready)"
    PROTOCOL="http"
fi

# Success message
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         ✅  DEPLOYMENT SELESAI!  ✅                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${GREEN}🎉 Aplikasi E-Raport sudah online!${NC}"
echo ""
echo -e "${YELLOW}Akses aplikasi di:${NC}"
echo -e "  ${CYAN}${PROTOCOL}://${DOMAIN}${NC}"
echo ""

if [ "$SKIP_SSL" = true ]; then
    echo -e "${YELLOW}⚠️  NEXT STEPS:${NC}"
    echo -e "  1. Setup DNS A Record di provider domain:"
    echo -e "     ${CYAN}@ → $SERVER_IP${NC}"
    echo -e "     ${CYAN}www → $SERVER_IP${NC}"
    echo ""
    echo -e "  2. Tunggu DNS propagasi (5 menit - 24 jam)"
    echo ""
    echo -e "  3. Setup SSL certificate:"
    echo -e "     ${CYAN}./setup-ssl.sh${NC}"
    echo ""
fi

echo -e "${GREEN}Login Default:${NC}"
echo -e "  Username: ${CYAN}admin${NC}"
echo -e "  Password: ${CYAN}admin123${NC}"
echo ""
echo -e "${RED}⚠️  SEGERA UBAH PASSWORD SETELAH LOGIN!${NC}"
echo ""

echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "  ${CYAN}docker-compose logs -f${NC}     # View logs"
echo -e "  ${CYAN}docker-compose restart${NC}     # Restart"
echo -e "  ${CYAN}docker-compose ps${NC}          # Status"
echo -e "  ${CYAN}make backup${NC}                # Backup database"
echo ""

echo -e "${BLUE}📚 Dokumentasi:${NC}"
echo -e "  - PRODUCTION_DEPLOYMENT.md - Panduan lengkap"
echo -e "  - DNS_SETUP_GUIDE.md - Setup DNS"
echo -e "  - SSL_SETUP_GUIDE.md - Setup SSL"
echo ""

echo -e "${GREEN}Happy deployment! 🚀${NC}"
echo ""
