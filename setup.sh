#!/bin/bash

# Script untuk initial setup aplikasi E-Raport
# Mempermudah setup pertama kali

clear

# Warna
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🎓  E-RAPORT APPLICATION SETUP  🎓                ║
║                                                           ║
║     Sistem Informasi Raport Digital                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${GREEN}Selamat datang di E-Raport Setup Wizard!${NC}"
echo -e "${YELLOW}Script ini akan membantu Anda setup aplikasi.${NC}"
echo ""

# Check Docker
echo -e "${BLUE}[1/6]${NC} Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker tidak terinstall!${NC}"
    echo -e "${YELLOW}Install Docker terlebih dahulu:${NC}"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose tidak terinstall!${NC}"
    echo -e "${YELLOW}Install Docker Compose terlebih dahulu:${NC}"
    echo "  sudo apt install docker-compose -y"
    exit 1
fi

echo -e "${GREEN}✓ Docker dan Docker Compose terinstall${NC}"
echo ""

# Environment Setup
echo -e "${BLUE}[2/6]${NC} Setting up environment variables..."

if [ -f .env ]; then
    echo -e "${YELLOW}⚠ File .env sudah ada${NC}"
    read -p "Overwrite? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo -e "${YELLOW}Menggunakan .env yang sudah ada${NC}"
    else
        rm .env
    fi
fi

if [ ! -f .env ]; then
    # Generate secret key
    echo -e "${YELLOW}Generating secure secret key...${NC}"
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    
    # Get domain
    echo ""
    echo -e "${CYAN}Apakah Anda sudah punya domain?${NC}"
    echo "  1) Ya, saya punya domain"
    echo "  2) Tidak, gunakan IP saja (development)"
    read -p "Pilih (1/2): " domain_choice
    
    if [ "$domain_choice" = "1" ]; then
        read -p "Masukkan domain Anda (contoh: raport.sekolah.id): " DOMAIN
        read -p "Masukkan email untuk SSL certificate: " EMAIL
        MODE="production"
    else
        DOMAIN=$(hostname -I | awk '{print $1}')
        EMAIL="admin@localhost"
        MODE="development"
    fi
    
    # Create .env
    cat > .env << EOL
# Flask Configuration
FLASK_CONFIG=${MODE}
SECRET_KEY=${SECRET_KEY}

# Database
DATABASE_URL=sqlite:////app/storage/data.sqlite

# Domain Configuration
DOMAIN=${DOMAIN}
EMAIL=${EMAIL}
EOL
    
    echo -e "${GREEN}✓ File .env created${NC}"
else
    source .env
fi

echo ""

# Create directories
echo -e "${BLUE}[3/6]${NC} Creating required directories..."
mkdir -p storage/backups
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p nginx/conf.d

echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Show configuration
echo -e "${BLUE}[4/6]${NC} Configuration Summary:"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  Mode:      ${GREEN}${FLASK_CONFIG:-production}${NC}"
echo -e "  Domain:    ${GREEN}${DOMAIN}${NC}"
echo -e "  Email:     ${GREEN}${EMAIL}${NC}"
echo -e "  Database:  ${GREEN}SQLite${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

read -p "Lanjutkan dengan konfigurasi ini? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo -e "${RED}Setup dibatalkan${NC}"
    exit 1
fi

echo ""

# Build containers
echo -e "${BLUE}[5/6]${NC} Building Docker containers..."
echo -e "${YELLOW}This may take a few minutes...${NC}"
docker-compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Containers built successfully${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

echo ""

# Start containers
echo -e "${BLUE}[6/6]${NC} Starting containers..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Containers started${NC}"
else
    echo -e "${RED}✗ Failed to start containers${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Waiting for application to be ready...${NC}"
sleep 5

# Show status
echo ""
echo -e "${BLUE}Container Status:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              ✅  SETUP SELESAI!  ✅                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Instructions
echo ""
if [ "$FLASK_CONFIG" = "production" ] || [ "$MODE" = "production" ]; then
    echo -e "${GREEN}Aplikasi sudah running!${NC}"
    echo ""
    echo -e "${YELLOW}Langkah selanjutnya:${NC}"
    echo ""
    echo -e "  ${BLUE}1.${NC} Test HTTP access:"
    echo -e "     ${CYAN}http://${DOMAIN}${NC}"
    echo ""
    echo -e "  ${BLUE}2.${NC} Setup SSL certificate (jika domain sudah pointing):"
    echo -e "     ${CYAN}./setup-ssl.sh${NC}"
    echo ""
    echo -e "  ${BLUE}3.${NC} Setelah SSL setup, akses:"
    echo -e "     ${CYAN}https://${DOMAIN}${NC}"
else
    echo -e "${GREEN}Development environment ready!${NC}"
    echo ""
    echo -e "${YELLOW}Akses aplikasi di:${NC}"
    echo -e "  ${CYAN}http://${DOMAIN}${NC}"
fi

echo ""
echo -e "${GREEN}Login Default:${NC}"
echo -e "  Username: ${CYAN}admin${NC}"
echo -e "  Password: ${CYAN}admin123${NC}"
echo ""
echo -e "${RED}⚠️  PENTING: Segera ubah password setelah login!${NC}"

echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "  ${CYAN}docker-compose logs -f${NC}     # View logs"
echo -e "  ${CYAN}docker-compose restart${NC}     # Restart application"
echo -e "  ${CYAN}docker-compose down${NC}        # Stop application"
echo -e "  ${CYAN}make help${NC}                  # Show all available commands"

echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""
