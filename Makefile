# Makefile for E-Raport Application
# Makes common Docker commands easier to remember

.PHONY: help build up down restart logs clean test-local setup-ssl backup restore

# Colors for better readability
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)E-Raport Docker Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2}'

## Production Commands

build: ## Build production containers
	@echo "$(YELLOW)Building production containers...$(NC)"
	docker-compose build

up: ## Start production containers
	@echo "$(YELLOW)Starting production containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Containers started!$(NC)"
	@sleep 2
	@make status

down: ## Stop production containers
	@echo "$(YELLOW)Stopping containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)Containers stopped!$(NC)"

restart: ## Restart production containers
	@echo "$(YELLOW)Restarting containers...$(NC)"
	docker-compose restart
	@echo "$(GREEN)Containers restarted!$(NC)"

status: ## Show container status
	@echo "$(BLUE)Container Status:$(NC)"
	@docker-compose ps

logs: ## Show logs (use 'make logs service=web' for specific service)
	@docker-compose logs -f $(service)

## Development Commands

dev-up: ## Start development environment
	@echo "$(YELLOW)Starting development environment...$(NC)"
	docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)Dev environment started at http://localhost:5005$(NC)"

dev-down: ## Stop development environment
	docker-compose -f docker-compose.dev.yml down

dev-logs: ## Show development logs
	docker-compose -f docker-compose.dev.yml logs -f

## SSL & Security

setup-ssl: ## Setup SSL certificate with Let's Encrypt
	@echo "$(YELLOW)Setting up SSL certificate...$(NC)"
	@chmod +x setup-ssl.sh
	@./setup-ssl.sh

renew-ssl: ## Manually renew SSL certificate
	@echo "$(YELLOW)Renewing SSL certificate...$(NC)"
	docker-compose run --rm certbot renew
	docker-compose restart nginx
	@echo "$(GREEN)SSL certificate renewed!$(NC)"

check-ssl: ## Check SSL certificate expiry
	@docker-compose exec certbot certbot certificates

## Database & Backup

backup: ## Backup database
	@echo "$(YELLOW)Creating database backup...$(NC)"
	@mkdir -p storage/backups
	@docker-compose exec web cp /app/storage/data.sqlite /app/storage/backups/backup-$(shell date +%Y%m%d-%H%M%S).sqlite
	@echo "$(GREEN)Backup created in storage/backups/$(NC)"

restore: ## Restore database (use 'make restore file=backup-20260105.sqlite')
	@echo "$(YELLOW)Restoring database from $(file)...$(NC)"
	@docker cp storage/backups/$(file) raport_app:/app/storage/data.sqlite
	@docker-compose restart web
	@echo "$(GREEN)Database restored and application restarted!$(NC)"

## Maintenance

clean: ## Remove all containers, images, and volumes
	@echo "$(YELLOW)Cleaning up...$(NC)"
	docker-compose down -v --rmi all
	@echo "$(GREEN)Cleanup complete!$(NC)"

update: ## Update application (pull latest code and rebuild)
	@echo "$(YELLOW)Updating application...$(NC)"
	git pull
	docker-compose up -d --build
	@echo "$(GREEN)Application updated!$(NC)"

shell: ## Access Flask application shell
	docker-compose exec web /bin/sh

db-shell: ## Access database shell
	docker-compose exec web sqlite3 /app/storage/data.sqlite

nginx-shell: ## Access Nginx shell
	docker-compose exec nginx /bin/sh

nginx-test: ## Test Nginx configuration
	docker-compose exec nginx nginx -t

nginx-reload: ## Reload Nginx configuration
	docker-compose exec nginx nginx -s reload

## Testing & Debugging

test-local: ## Test application locally
	@chmod +x test-local.sh
	@./test-local.sh

inspect: ## Inspect containers
	docker-compose ps -a
	@echo ""
	@echo "$(BLUE)Network:$(NC)"
	docker network inspect web_app_raport_network | grep -A 5 "Containers"

## Default target
.DEFAULT_GOAL := help
