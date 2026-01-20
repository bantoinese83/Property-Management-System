# Deployment & Troubleshooting Guide

Complete deployment instructions and common issues/solutions.

---

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment (AWS EC2)](#production-deployment-aws-ec2)
4. [Troubleshooting Common Issues](#troubleshooting-common-issues)
5. [Performance Optimization](#performance-optimization)
6. [Backup & Recovery](#backup--recovery)

---

## Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Git
- Virtual environment (venv or conda)

### Step-by-Step Backend Setup

```bash
# 1. Clone repository
git clone <your-repo-url>
cd property-management-system

# 2. Create Python virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Create .env file from example
cp .env.example .env

# 7. Update .env with your configuration
# Edit .env with:
# DEBUG=True
# SECRET_KEY=your-secret-key-here
# DATABASE_URL=postgresql://user:password@localhost:5432/property_mgmt
# ALLOWED_HOSTS=localhost,127.0.0.1

# 8. Create PostgreSQL database
createdb property_mgmt

# 9. Run Django migrations
python manage.py makemigrations
python manage.py migrate

# 10. Create superuser
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (your secure password)

# 11. Load sample data (optional)
python manage.py create_demo_data

# 12. Collect static files
python manage.py collectstatic --noinput

# 13. Run development server
python manage.py runserver
# Backend will be running at http://localhost:8000
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd property-management-frontend

# 2. Install dependencies
npm install

# 3. Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Property Management System
VITE_APP_VERSION=1.0.0
EOF

# 4. Run development server
npm run dev
# Frontend will be at http://localhost:5173

# 5. In another terminal, start backend
# (from project root)
source venv/bin/activate  # or venv\Scripts\activate on Windows
python manage.py runserver
```

### Verify Setup

```bash
# Test backend API
curl http://localhost:8000/api/token/ -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# Should return tokens:
# {"access":"eyJ...","refresh":"eyJ..."}

# Test frontend
open http://localhost:5173
# Should see login page
```

---

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed

### docker-compose.yml (Complete)

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: property-mgmt-db
    environment:
      POSTGRES_DB: property_mgmt
      POSTGRES_USER: ${DB_USER:-property_user}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secure_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U property_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - property-mgmt-network

  # Django Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: property-mgmt-backend
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120"
    environment:
      DEBUG: ${DEBUG:-False}
      SECRET_KEY: ${SECRET_KEY:-your-secret-key}
      DATABASE_URL: postgresql://${DB_USER:-property_user}:${DB_PASSWORD:-secure_password}@db:5432/property_mgmt
      ALLOWED_HOSTS: ${ALLOWED_HOSTS:-localhost,127.0.0.1}
      CORS_ALLOWED_ORIGINS: ${CORS_ALLOWED_ORIGINS:-http://localhost:3000,http://localhost:5173}
    volumes:
      - .:/code
      - static_volume:/code/staticfiles
      - media_volume:/code/media
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    networks:
      - property-mgmt-network

  # React Frontend
  frontend:
    build:
      context: ./property-management-frontend
      dockerfile: Dockerfile
    container_name: property-mgmt-frontend
    environment:
      VITE_API_URL: ${VITE_API_URL:-http://localhost:8000/api}
    volumes:
      - ./property-management-frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    depends_on:
      - backend
    networks:
      - property-mgmt-network

  # Nginx Reverse Proxy (Optional)
  nginx:
    image: nginx:alpine
    container_name: property-mgmt-nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/code/staticfiles:ro
      - media_volume:/code/media:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
    networks:
      - property-mgmt-network

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  property-mgmt-network:
    driver: bridge
```

### Dockerfile (Backend)

```dockerfile
FROM python:3.11-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /code
USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Dockerfile (Frontend)

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app
RUN npm install -g serve

COPY --from=builder /app/dist ./dist

EXPOSE 5173

CMD ["serve", "-s", "dist", "-l", "5173"]
```

### Running Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load demo data
docker-compose exec backend python manage.py create_demo_data

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Production Deployment (AWS EC2)

### Step 1: Launch EC2 Instance

```bash
# 1. Launch Ubuntu 22.04 LTS instance
# 2. Create security group allowing:
#    - SSH (22) from your IP
#    - HTTP (80) from anywhere
#    - HTTPS (443) from anywhere
#    - PostgreSQL (5432) from within VPC only

# 3. Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip
```

### Step 2: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib \
    nginx supervisor git curl \
    build-essential libssl-dev libffi-dev

# Install Docker (optional but recommended)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

### Step 3: Set Up Application

```bash
# Clone repository
cd /home/ubuntu
git clone <your-repo-url> app
cd app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Create .env file
cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
DATABASE_URL=postgresql://property_user:secure_password@localhost:5432/property_mgmt
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
AWS_S3_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
EOF

# Set permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/app
chmod 600 .env
```

### Step 4: Set Up PostgreSQL

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE property_mgmt;
CREATE USER property_user WITH PASSWORD 'secure_password';
ALTER ROLE property_user SET client_encoding TO 'utf8';
ALTER ROLE property_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE property_user SET default_transaction_deferrable TO on;
ALTER ROLE property_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE property_mgmt TO property_user;
\q
EOF

# Run migrations
cd /home/ubuntu/app
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 5: Configure Nginx

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/property-mgmt << EOF
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    client_max_body_size 100M;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    client_max_body_size 100M;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias /home/ubuntu/app/staticfiles/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /home/ubuntu/app/media/;
        expires 7d;
    }

    # API requests
    location /api/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Admin panel
    location /admin/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        root /home/ubuntu/app/frontend-build;
        try_files $uri /index.html;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/property-mgmt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Configure SSL (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Step 7: Configure Gunicorn with Supervisor

```bash
# Create Supervisor config
sudo tee /etc/supervisor/conf.d/property-mgmt.conf << EOF
[program:property-mgmt]
directory=/home/ubuntu/app
command=/home/ubuntu/app/venv/bin/gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --access-logfile /home/ubuntu/app/logs/access.log \
    --error-logfile /home/ubuntu/app/logs/error.log
user=ubuntu
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
environment=PATH="/home/ubuntu/app/venv/bin",DB_PASS="secure_password"
EOF

# Create logs directory
mkdir -p /home/ubuntu/app/logs

# Start Supervisor
sudo systemctl enable supervisor
sudo systemctl start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start property-mgmt
```

### Step 8: Build and Deploy Frontend

```bash
# Build React frontend
cd /home/ubuntu/app/property-management-frontend
npm install
npm run build

# Copy to Nginx root
sudo cp -r dist /home/ubuntu/app/frontend-build

# Ensure permissions
sudo chown -R www-data:www-data /home/ubuntu/app/frontend-build
```

### Step 9: Verification

```bash
# Check services
sudo systemctl status nginx
sudo systemctl status postgresql
sudo supervisorctl status property-mgmt

# Check logs
sudo tail -f /home/ubuntu/app/logs/error.log
sudo tail -f /var/log/nginx/error.log

# Verify database
python manage.py shell
# >>> from django.contrib.auth.models import User
# >>> User.objects.count()
```

---

## Troubleshooting Common Issues

### Issue 1: Django Returns 500 Error

```bash
# Check Django logs
docker-compose logs backend
# or
tail -f /home/ubuntu/app/logs/error.log

# Common causes:
# 1. Database not initialized
python manage.py migrate

# 2. Missing environment variables
cat .env

# 3. Static files not collected
python manage.py collectstatic --noinput

# 4. Permission issues
sudo chown -R ubuntu:ubuntu /home/ubuntu/app
```

### Issue 2: PostgreSQL Connection Refused

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U property_user -d property_mgmt -h localhost

# Check credentials in .env
cat .env | grep DATABASE_URL

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Issue 3: React App Shows Blank Page

```bash
# Check browser console for errors
# Open browser DevTools (F12) → Console tab

# Common causes:
# 1. Frontend not built
cd property-management-frontend
npm run build

# 2. Wrong API URL
# Check .env file
cat .env | grep VITE_API_URL

# 3. Nginx not serving correctly
sudo nginx -t
sudo systemctl reload nginx
```

### Issue 4: CORS Errors

```bash
# Add domain to CORS_ALLOWED_ORIGINS in .env
CORS_ALLOWED_ORIGINS=https://your-domain.com,http://localhost:5173

# Restart Django
# Docker: docker-compose restart backend
# Manual: sudo supervisorctl restart property-mgmt
```

### Issue 5: Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --noinput --clear

# Check Nginx config
sudo nginx -t

# Verify file permissions
ls -la staticfiles/
sudo chown -R www-data:www-data staticfiles/
```

---

## Performance Optimization

### Database Optimization

```python
# In Django views, use select_related and prefetch_related
from django.db.models import Prefetch

# Bad (N+1 queries):
for lease in Lease.objects.all():
    print(lease.tenant.first_name)  # Extra query per lease

# Good:
Lease.objects.select_related('tenant').all()

# For reverse foreign keys:
properties = Property.objects.prefetch_related('leases').all()
```

### Caching with Redis

```bash
# Install Redis
docker run -d -p 6379:6379 redis:latest

# Or on server:
sudo apt install redis-server
sudo systemctl start redis-server
```

**Add to Django settings:**

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'property_mgmt',
        'TIMEOUT': 300,
    }
}

# Use cache decorator
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def get_properties(request):
    ...
```

### Frontend Optimization

```javascript
// Lazy load components
const PropertyList = React.lazy(() => import('./components/PropertyList'));

// Memoize components to prevent unnecessary re-renders
const PropertyCard = React.memo(({ property }) => (
  ...
));
```

---

## Backup & Recovery

### PostgreSQL Backup

```bash
# Full backup
pg_dump property_mgmt > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
pg_dump property_mgmt | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Scheduled backup (daily at 2 AM)
0 2 * * * pg_dump property_mgmt | gzip > /backups/property_mgmt_$(date +\%Y\%m\%d).sql.gz
```

### Restore from Backup

```bash
# Restore database
psql property_mgmt < backup_20240101_120000.sql

# Or from compressed file
gunzip -c backup_20240101_120000.sql.gz | psql property_mgmt
```

### Media Files Backup (S3)

```bash
# Sync media to S3
aws s3 sync /home/ubuntu/app/media s3://your-bucket/media/

# Restore from S3
aws s3 sync s3://your-bucket/media/ /home/ubuntu/app/media/
```

---

**Deployment Complete!** Your application is now running in production.

For issues, check logs first, then refer to this troubleshooting guide.
