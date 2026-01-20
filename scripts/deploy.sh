#!/bin/bash

# Property Management System - Production Deployment Script
# Usage: ./deploy.sh [environment]
# Environment: staging | production

set -e

ENVIRONMENT=${1:-production}
PROJECT_DIR="/home/ubuntu/pms"
BACKUP_DIR="/home/ubuntu/backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting deployment to ${ENVIRONMENT}${NC}"

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo -e "${RED}❌ Invalid environment. Use 'staging' or 'production'${NC}"
    exit 1
fi

# Navigate to project directory
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${NC}"
    exit 1
}

# Create backup
echo -e "${YELLOW}📦 Creating database backup...${NC}"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
docker-compose exec -T db pg_dump -U property_user property_mgmt > "$BACKUP_FILE" || {
    echo -e "${RED}❌ Database backup failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Database backup created: $BACKUP_FILE${NC}"

# Pull latest changes
echo -e "${YELLOW}📥 Pulling latest code...${NC}"
git fetch origin
git checkout "${ENVIRONMENT}"
git pull origin "${ENVIRONMENT}"

# Build and deploy
echo -e "${YELLOW}🐳 Building and deploying containers...${NC}"
if [[ "$ENVIRONMENT" == "staging" ]]; then
    docker-compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.staging.yml pull
    docker-compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.staging.yml up -d --build
else
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
fi

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 30

# Run migrations
echo -e "${YELLOW}🗄️ Running database migrations...${NC}"
if [[ "$ENVIRONMENT" == "staging" ]]; then
    docker-compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.staging.yml exec -T backend python manage.py migrate --check || {
        docker-compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.staging.yml exec -T backend python manage.py migrate
    }
else
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python manage.py migrate --check || {
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python manage.py migrate
    }
fi

# Collect static files
echo -e "${YELLOW}📂 Collecting static files...${NC}"
if [[ "$ENVIRONMENT" == "staging" ]]; then
    docker-compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.staging.yml exec -T backend python manage.py collectstatic --noinput --clear
else
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput --clear
fi

# Run tests
echo -e "${YELLOW}🧪 Running tests...${NC}"
if [[ "$ENVIRONMENT" == "staging" ]]; then
    docker-compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.staging.yml exec -T backend python manage.py test --keepdb || {
        echo -e "${RED}❌ Tests failed, rolling back...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.staging.yml exec -T db psql -U property_user -d property_mgmt < "$BACKUP_FILE"
        exit 1
    }
fi

# Health check
echo -e "${YELLOW}🏥 Running health checks...${NC}"
HEALTH_CHECK_URL="http://localhost/api/"
if [[ "$ENVIRONMENT" == "production" ]]; then
    HEALTH_CHECK_URL="https://your-domain.com/api/"
fi

if curl -f -s "$HEALTH_CHECK_URL" > /dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed, rolling back...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db psql -U property_user -d property_mgmt < "$BACKUP_FILE"
    exit 1
fi

# Clean up old images and containers
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
docker system prune -f

# Send notification (optional)
echo -e "${GREEN}✅ Deployment to ${ENVIRONMENT} completed successfully!${NC}"
echo -e "${GREEN}🌐 Application is running at: $(if [[ "$ENVIRONMENT" == "production" ]]; then echo "https://your-domain.com"; else echo "http://localhost"; fi)${NC}"

# Log deployment
echo "$(date): Deployment to ${ENVIRONMENT} completed successfully" >> "$PROJECT_DIR/deploy.log"