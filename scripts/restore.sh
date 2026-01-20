#!/bin/bash

# Property Management System - Database Restore Script
# Usage: ./restore.sh <backup_directory>
# Example: ./restore.sh /home/ubuntu/backups/20241201_120000

set -e

# Configuration
PROJECT_DIR="/home/ubuntu/pms"
BACKUP_DIR="$1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
LOG_FILE="$PROJECT_DIR/restore.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Validate input
if [ -z "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Usage: $0 <backup_directory>${NC}"
    echo -e "${YELLOW}Example: $0 /home/ubuntu/backups/20241201_120000${NC}"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

# Show backup manifest
if [ -f "$BACKUP_DIR/manifest.txt" ]; then
    echo -e "${BLUE}📋 Backup Manifest:${NC}"
    cat "$BACKUP_DIR/manifest.txt"
    echo
fi

echo -e "${YELLOW}⚠️  WARNING: This will overwrite the current database!${NC}"
read -p "Are you sure you want to continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${RED}❌ Restore cancelled by user${NC}"
    exit 1
fi

log "🔄 Starting database restore from: $BACKUP_DIR"

# Stop application to prevent data corruption
log "🛑 Stopping application services..."
docker-compose down
log "✅ Application services stopped"

# Database restore
if [ -f "$BACKUP_DIR/database.sql.gz" ]; then
    log "🗄️ Restoring database..."
    gunzip -c "$BACKUP_DIR/database.sql.gz" | docker-compose exec -T db psql -U property_user -d property_mgmt
    log "✅ Database restored successfully"
elif [ -f "$BACKUP_DIR/database.sql" ]; then
    log "🗄️ Restoring database..."
    docker-compose exec -T db psql -U property_user -d property_mgmt < "$BACKUP_DIR/database.sql"
    log "✅ Database restored successfully"
else
    log "❌ Database backup file not found"
    exit 1
fi

# Media files restore
if [ -f "$BACKUP_DIR/media.tar.gz" ]; then
    log "📁 Restoring media files..."
    # Create backup of current media files
    if [ -d "$PROJECT_DIR/backend/media" ]; then
        mv "$PROJECT_DIR/backend/media" "$PROJECT_DIR/backend/media.backup.$(date +%Y%m%d_%H%M%S)"
    fi

    # Extract media files
    mkdir -p "$PROJECT_DIR/backend/media"
    tar -xzf "$BACKUP_DIR/media.tar.gz" -C "$PROJECT_DIR/backend/media"
    log "✅ Media files restored successfully"
else
    log "⚠️ Media files backup not found, skipping..."
fi

# Static files restore (usually regenerated, but restore if needed)
if [ -f "$BACKUP_DIR/static.tar.gz" ]; then
    log "📂 Restoring static files..."
    mkdir -p "$PROJECT_DIR/backend/staticfiles"
    tar -xzf "$BACKUP_DIR/static.tar.gz" -C "$PROJECT_DIR/backend/"
    log "✅ Static files restored successfully"
else
    log "ℹ️ Static files backup not found, will be regenerated"
fi

# Restart application
log "🚀 Restarting application services..."
docker-compose up -d

# Wait for services to start
log "⏳ Waiting for services to start..."
sleep 30

# Run migrations (in case schema changed)
log "🗄️ Running database migrations..."
docker-compose exec backend python manage.py migrate

# Collect static files
log "📂 Collecting static files..."
docker-compose exec backend python manage.py collectstatic --noinput

# Health check
log "🏥 Running health check..."
if curl -f -s http://localhost/api/ > /dev/null 2>&1; then
    log "✅ Health check passed - application is running"
else
    log "❌ Health check failed - please check application logs"
    log "Run: docker-compose logs backend"
    exit 1
fi

log "🎉 Restore completed successfully!"
log "🌐 Application should be available at: http://localhost"

# Optional: Clean up old media backup
log "🧹 Cleaning up temporary files..."
find "$PROJECT_DIR/backend" -name "media.backup.*" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true

echo
echo -e "${GREEN}✅ Restore Summary:${NC}"
echo -e "  📍 Backup Source: $BACKUP_DIR"
echo -e "  🗄️ Database: Restored"
echo -e "  📁 Media Files: $([ -f "$BACKUP_DIR/media.tar.gz" ] && echo "Restored" || echo "Not found")"
echo -e "  📂 Static Files: $([ -f "$BACKUP_DIR/static.tar.gz" ] && echo "Restored" || echo "Regenerated")"
echo -e "  🌐 Application: Running at http://localhost"
echo
echo -e "${YELLOW}📞 Next Steps:${NC}"
echo -e "  1. Verify application functionality"
echo -e "  2. Check that all data is restored correctly"
echo -e "  3. Update any configuration files if needed"
echo -e "  4. Notify users that system is back online"

exit 0