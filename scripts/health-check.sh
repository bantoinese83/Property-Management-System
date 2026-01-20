#!/bin/bash

# Property Management System - Health Check Script
# This script performs comprehensive health checks on all services

set -e

# Configuration
PROJECT_DIR="/home/ubuntu/pms"
API_URL="http://localhost/api"
FRONTEND_URL="http://localhost"
DB_HOST="localhost"
DB_PORT="5432"
DB_USER="property_user"
DB_NAME="property_mgmt"
REDIS_HOST="localhost"
REDIS_PORT="6379"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Results tracking
CHECKS_PASSED=0
CHECKS_FAILED=0

log_check() {
    local name="$1"
    local status="$2"
    local message="$3"

    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $name: $message${NC}"
        ((CHECKS_PASSED++))
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $name: $message${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}❌ $name: $message${NC}"
        ((CHECKS_FAILED++))
    fi
}

echo -e "${BLUE}🏥 Property Management System - Health Check${NC}"
echo -e "${BLUE}================================================${NC}"
echo "Date: $(date)"
echo "Server: $(hostname)"
echo

# Docker services check
echo -e "${YELLOW}🐳 Docker Services:${NC}"
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        log_check "Docker Services" "PASS" "Services are running"
    else
        log_check "Docker Services" "FAIL" "No services running"
    fi

    # Check individual containers
    services=("pms-db" "pms-redis" "pms-backend" "pms-frontend" "pms-nginx")
    for service in "${services[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "^${service}$"; then
            log_check "$service Container" "PASS" "Running"
        else
            log_check "$service Container" "FAIL" "Not running"
        fi
    done
else
    log_check "Docker" "FAIL" "Docker not installed or not running"
fi

echo

# Database connectivity
echo -e "${YELLOW}🗄️ Database:${NC}"
if command -v psql &> /dev/null; then
    if PGPASSWORD="secure_password" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" &> /dev/null; then
        log_check "Database Connection" "PASS" "Connected successfully"

        # Check database size
        DB_SIZE=$(PGPASSWORD="secure_password" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null | tr -d ' ')
        log_check "Database Size" "INFO" "$DB_SIZE"

        # Check table counts
        TABLE_COUNT=$(PGPASSWORD="secure_password" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
        log_check "Tables Count" "INFO" "$TABLE_COUNT tables"
    else
        log_check "Database Connection" "FAIL" "Cannot connect to database"
    fi
else
    log_check "PostgreSQL Client" "FAIL" "psql command not found"
fi

echo

# Redis check
echo -e "${YELLOW}🔄 Redis:${NC}"
if command -v redis-cli &> /dev/null; then
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping &> /dev/null; then
        log_check "Redis Connection" "PASS" "Connected successfully"

        # Check Redis memory usage
        REDIS_MEMORY=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" info memory | grep "used_memory_human" | cut -d: -f2 | tr -d '\r')
        log_check "Redis Memory" "INFO" "$REDIS_MEMORY used"
    else
        log_check "Redis Connection" "FAIL" "Cannot connect to Redis"
    fi
else
    log_check "Redis Client" "FAIL" "redis-cli command not found"
fi

echo

# API health check
echo -e "${YELLOW}🔌 API Endpoints:${NC}"
if command -v curl &> /dev/null; then
    # Main API health check
    if curl -f -s --max-time 10 "$API_URL/" > /dev/null; then
        log_check "API Health" "PASS" "API responding"

        # Check specific endpoints
        endpoints=("$API_URL/properties/" "$API_URL/tenants/" "$API_URL/leases/")
        for endpoint in "${endpoints[@]}"; do
            if curl -f -s --max-time 5 "$endpoint" > /dev/null; then
                endpoint_name=$(basename "$endpoint" | sed 's/\///g')
                log_check "${endpoint_name} API" "PASS" "Endpoint accessible"
            else
                endpoint_name=$(basename "$endpoint" | sed 's/\///g')
                log_check "${endpoint_name} API" "FAIL" "Endpoint not accessible"
            fi
        done
    else
        log_check "API Health" "FAIL" "API not responding"
    fi

    # Frontend health check
    if curl -f -s --max-time 10 "$FRONTEND_URL" > /dev/null; then
        log_check "Frontend" "PASS" "Frontend responding"
    else
        log_check "Frontend" "FAIL" "Frontend not responding"
    fi
else
    log_check "HTTP Client" "FAIL" "curl command not found"
fi

echo

# Disk space check
echo -e "${YELLOW}💾 Disk Space:${NC}"
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    log_check "Disk Usage" "PASS" "${DISK_USAGE}% used"
elif [ "$DISK_USAGE" -lt 90 ]; then
    log_check "Disk Usage" "WARN" "${DISK_USAGE}% used"
else
    log_check "Disk Usage" "FAIL" "${DISK_USAGE}% used - CRITICAL"
fi

echo

# Backup check
echo -e "${YELLOW}📦 Recent Backups:${NC}"
BACKUP_DIR="/home/ubuntu/backups"
if [ -d "$BACKUP_DIR" ]; then
    # Check for recent backups (last 24 hours)
    RECENT_BACKUPS=$(find "$BACKUP_DIR" -name "20*" -type d -mtime -1 2>/dev/null | wc -l)
    if [ "$RECENT_BACKUPS" -gt 0 ]; then
        LATEST_BACKUP=$(find "$BACKUP_DIR" -name "20*" -type d -mtime -1 -print0 2>/dev/null | xargs -0 ls -td | head -1)
        BACKUP_SIZE=$(du -sh "$LATEST_BACKUP" 2>/dev/null | cut -f1)
        log_check "Recent Backup" "PASS" "Found $RECENT_BACKUPS backup(s), latest: $BACKUP_SIZE"
    else
        log_check "Recent Backup" "WARN" "No backups in the last 24 hours"
    fi
else
    log_check "Backup Directory" "FAIL" "Backup directory not found"
fi

echo

# Application logs check
echo -e "${YELLOW}📄 Application Logs:${NC}"
LOG_DIR="$PROJECT_DIR/logs"
if [ -d "$LOG_DIR" ]; then
    # Check for recent errors in logs
    ERROR_COUNT=$(find "$LOG_DIR" -name "*.log" -exec grep -l "ERROR\|CRITICAL" {} \; 2>/dev/null | wc -l)
    if [ "$ERROR_COUNT" -eq 0 ]; then
        log_check "Application Logs" "PASS" "No recent errors found"
    else
        log_check "Application Logs" "WARN" "$ERROR_COUNT log file(s) contain errors"
    fi
else
    log_check "Log Directory" "INFO" "Log directory not found (may be in containers)"
fi

echo
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}✅ Checks Passed: $CHECKS_PASSED${NC}"
if [ "$CHECKS_FAILED" -gt 0 ]; then
    echo -e "${RED}❌ Checks Failed: $CHECKS_FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}🎉 All health checks passed!${NC}"
    exit 0
fi