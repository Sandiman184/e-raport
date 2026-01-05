#!/bin/bash

# Manual Docker Compose Installation Script
# Use this if automatic installation in deploy-production.sh fails

set -e

echo "🔧 Manual Docker Compose Installation"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed!"
    echo "Please install Docker first:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Method 1: Try standalone binary (most reliable)
echo "Method 1: Installing standalone Docker Compose binary..."
echo ""

# Get latest version
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d '"' -f 4)
echo "Latest version: $COMPOSE_VERSION"

# Download
echo "Downloading..."
sudo curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify
if /usr/local/bin/docker-compose --version; then
    echo ""
    echo "✅ Docker Compose installed successfully!"
    echo ""
    echo "Installed version:"
    /usr/local/bin/docker-compose --version
    echo ""
    echo "You can now run:"
    echo "  ./deploy-production.sh"
    exit 0
else
    echo "❌ Installation failed via standalone binary"
    echo ""
fi

# Method 2: Try with pip (fallback)
echo "Method 2: Trying installation via pip..."

if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    sudo apt-get update
    sudo apt-get install python3-pip -y
    sudo pip3 install docker-compose
    
    if docker-compose --version; then
        echo ""
        echo "✅ Docker Compose installed via pip!"
        docker-compose --version
        exit 0
    fi
fi

echo ""
echo "❌ All installation methods failed"
echo ""
echo "Please try manual installation:"
echo "1. Visit: https://docs.docker.com/compose/install/"
echo "2. Follow instructions for your OS"
echo ""
exit 1
