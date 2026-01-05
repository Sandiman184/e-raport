#!/bin/bash

# Quick fix script untuk install Docker Compose
# Jalankan ini di server jika dapat error "docker-compose: command not found"

echo "🔧 Installing Docker Compose..."

# Method 1: Try installing via apt (easiest)
echo "Method 1: Installing via apt..."
sudo apt update
sudo apt install docker-compose-plugin -y

# Method 2: If v1 is needed, install standalone binary
if ! command -v docker-compose &> /dev/null; then
    echo "Method 2: Installing standalone Docker Compose v2..."
    
    # Download latest version
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d '"' -f 4)
    
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Create symlink if needed
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

# Verify installation
echo ""
echo "✅ Verifying installation..."
docker compose version || docker-compose version

echo ""
echo "Docker Compose installed successfully! 🎉"
echo ""
echo "Now you can run deployment script again:"
echo "  ./deploy-production.sh"
