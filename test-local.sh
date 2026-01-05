#!/bin/bash

# Script untuk testing lokal sebelum deploy
# Gunakan ini untuk test aplikasi di local machine

echo "🧪 Starting Local Test..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found, creating from example..."
    cp .env.example .env
    echo "✅ .env created. Please edit it with your settings."
    echo ""
fi

# Build and start
echo "🔨 Building and starting containers..."
docker-compose up -d --build

# Wait for containers to be ready
echo "⏳ Waiting for containers to be ready..."
sleep 5

# Check status
echo ""
echo "📊 Container Status:"
docker-compose ps

# Show logs
echo ""
echo "📝 Application Logs (last 20 lines):"
docker-compose logs --tail=20 web

# Get IP
IP=$(hostname -I | awk '{print $1}')

echo ""
echo "=========================================="
echo "✅ Local test environment is ready!"
echo "=========================================="
echo ""
echo "Access your application at:"
echo "  http://localhost"
echo "  http://$IP"
echo ""
echo "Default login:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
