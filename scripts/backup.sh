#!/bin/bash

# Property Management System - Automated Backup Script
# This script creates backups of database and media files

set -e

# Configuration
BACKUP_ROOT="/home/ubuntu/backups"
PROJECT_DIR="/home/ubuntu/pms"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging
LOG_FILE="$BACKUP_ROOT/backup.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "🗂️ Starting backup process..."

# Database backup
log "💾 Creating database backup..."
if docker-compose exec -T db pg_dump -U property_user -d property_mgmt > "$BACKUP_DIR/database.sql"; then
    log "✅ Database backup completed"
    # Compress database backup
    gzip "$BACKUP_DIR/database.sql"
    log "📦 Database backup compressed"
else
    log "❌ Database backup failed"
    exit 1
fi

# Media files backup
log "📁 Creating media files backup..."
if tar -czf "$BACKUP_DIR/media.tar.gz" -C "$PROJECT_DIR/backend" media/ 2>/dev/null; then
    log "✅ Media files backup completed"
else
    log "⚠️ Media files backup failed or no media files found"
fi

# Static files backup (optional, since they're generated)
log "📂 Creating static files backup..."
if tar -czf "$BACKUP_DIR/static.tar.gz" -C "$PROJECT_DIR/backend" staticfiles/ 2>/dev/null; then
    log "✅ Static files backup completed"
else
    log "⚠️ Static files backup failed"
fi

# Configuration backup
log "⚙️ Creating configuration backup..."
cp "$PROJECT_DIR/docker-compose.yml" "$BACKUP_DIR/"
cp "$PROJECT_DIR/docker-compose.prod.yml" "$BACKUP_DIR/"
cp "$PROJECT_DIR/nginx.prod.conf" "$BACKUP_DIR/"
log "✅ Configuration backup completed"

# Create backup manifest
cat > "$BACKUP_DIR/manifest.txt" << EOF
Backup Information
==================
Timestamp: $TIMESTAMP
Date: $(date)
Server: $(hostname)
Project: Property Management System

Contents:
- database.sql.gz: PostgreSQL database dump
- media.tar.gz: User uploaded media files
- static.tar.gz: Static files
- docker-compose.yml: Docker Compose configuration
- docker-compose.prod.yml: Production configuration
- nginx.prod.conf: Nginx configuration

To restore:
1. Extract backup files
2. Restore database: gunzip database.sql.gz && psql -U property_user -d property_mgmt < database.sql
3. Restore media: tar -xzf media.tar.gz -C /path/to/project/backend/
4. Update configurations as needed
EOF

log "📋 Backup manifest created"

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "📊 Backup size: $BACKUP_SIZE"

# Cleanup old backups
log "🧹 Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_ROOT" -name "20*" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
DELETED_COUNT=$(find "$BACKUP_ROOT" -name "20*" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null | wc -l)
if [ "$DELETED_COUNT" -gt 0 ]; then
    log "🗑️ Cleaned up $DELETED_COUNT old backup(s)"
fi

# Verify backup integrity
log "🔍 Verifying backup integrity..."
if [ -f "$BACKUP_DIR/database.sql.gz" ]; then
    if gzip -t "$BACKUP_DIR/database.sql.gz"; then
        log "✅ Database backup integrity verified"
    else
        log "❌ Database backup integrity check failed"
        exit 1
    fi
fi

log "🎉 Backup completed successfully!"
log "📍 Backup location: $BACKUP_DIR"

# Optional: Upload to cloud storage (uncomment and configure)
# log "☁️ Uploading to cloud storage..."
# aws s3 cp "$BACKUP_DIR" s3://your-backup-bucket/backups/$TIMESTAMP --recursive
# log "✅ Backup uploaded to cloud storage"

# Send notification (optional - configure email or Slack)
# echo "Backup completed successfully on $(date)" | mail -s "PMS Backup Complete" admin@example.com

exit 0