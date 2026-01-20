#!/bin/bash

# Property Management System - Setup Automated Backups
# This script sets up cron jobs for automated backups

set -e

# Configuration
PROJECT_DIR="/home/ubuntu/pms"
BACKUP_SCRIPT="$PROJECT_DIR/scripts/backup.sh"
LOG_FILE="$PROJECT_DIR/backup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔄 Setting up automated backups...${NC}"

# Validate backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo -e "${RED}❌ Backup script not found: $BACKUP_SCRIPT${NC}"
    exit 1
fi

# Make scripts executable
chmod +x "$BACKUP_SCRIPT"
chmod +x "$PROJECT_DIR/scripts/restore.sh"

# Create backup directory if it doesn't exist
mkdir -p /home/ubuntu/backups

# Setup cron jobs
echo -e "${YELLOW}⏰ Setting up cron jobs...${NC}"

# Remove existing PMS backup cron jobs
(crontab -l 2>/dev/null | grep -v "backup.sh") | crontab -

# Add new cron jobs
(crontab -l 2>/dev/null; cat << EOF
# Property Management System - Automated Backups
# Daily backup at 2:00 AM
0 2 * * * $BACKUP_SCRIPT >> $LOG_FILE 2>&1

# Weekly full backup on Sundays at 3:00 AM
0 3 * * 0 $BACKUP_SCRIPT >> $LOG_FILE 2>&1

# Monthly backup on the 1st at 4:00 AM
0 4 1 * * $BACKUP_SCRIPT >> $LOG_FILE 2>&1
EOF
) | crontab -

echo -e "${GREEN}✅ Cron jobs configured successfully!${NC}"

# Display current cron jobs
echo -e "${BLUE}📋 Current backup cron jobs:${NC}"
crontab -l | grep backup.sh

echo
echo -e "${GREEN}🎉 Automated backup setup completed!${NC}"
echo
echo -e "${YELLOW}📅 Backup Schedule:${NC}"
echo -e "  🕐 Daily: 2:00 AM (every day)"
echo -e "  🕐 Weekly: 3:00 AM (Sundays)"
echo -e "  🕐 Monthly: 4:00 AM (1st of month)"
echo
echo -e "${BLUE}📍 Backup Location: /home/ubuntu/backups${NC}"
echo -e "${BLUE}📄 Log File: $LOG_FILE${NC}"
echo
echo -e "${YELLOW}🔧 Manual backup commands:${NC}"
echo -e "  📦 Run backup: $BACKUP_SCRIPT"
echo -e "  🔄 Restore backup: $PROJECT_DIR/scripts/restore.sh /path/to/backup"
echo
echo -e "${GREEN}💡 Tips:${NC}"
echo -e "  📊 Monitor backups: tail -f $LOG_FILE"
echo -e "  📂 Check backup sizes: du -sh /home/ubuntu/backups/*"
echo -e "  🧹 Old backups are automatically cleaned up (30 days retention)"

# Test backup script
echo -e "${YELLOW}🧪 Testing backup script...${NC}"
if "$BACKUP_SCRIPT" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backup script test successful${NC}"
else
    echo -e "${RED}⚠️ Backup script test failed - check logs${NC}"
fi

exit 0