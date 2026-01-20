# 🚀 Property Management System - Quick Setup Guide

**Get up and running in 5 minutes with Docker.**

---

## ⚡ **QUICK START (Docker - Recommended)**

### **Prerequisites**
- Docker & Docker Compose installed
- Git installed
- 4GB RAM available (recommended)

### **1. Clone & Setup**
```bash
# Clone repository
git clone <repository-url>
cd property-management-system

# Install development tools (optional but recommended)
pip install pre-commit
pre-commit install
```

### **2. Start Application**
```bash
# Start all services (database, backend, frontend)
docker-compose up -d

# Wait for services to start (~2 minutes)
# Check status: docker-compose ps
```

### **3. Load Demo Data**
```bash
# Populate database with sample data
docker-compose exec backend python manage.py create_demo_data
```

### **4. Access Application**
- **Frontend**: http://localhost (React app with hot reload)
- **Backend API**: http://localhost/api (Django REST API)
- **API Documentation**: http://localhost/api/docs (Swagger/OpenAPI)
- **Admin Panel**: http://localhost/admin (Django admin interface)

### **5. Demo Credentials**
- **Admin User**: `admin` / `admin123` (full system access)
- **Property Owner**: `owner` / `owner123` (property management access)

### **6. Demo Data**
The demo data includes:
- **1 Property**: "Downtown Apartment" with sample details
- **1 Tenant**: "John Doe" with contact information
- **1 Active Lease**: Current lease agreement with terms
- **Document Templates**: Pre-built lease and contract templates
- **Audit Logs**: Sample activity tracking entries

---

## 🏃‍♂️ **LOCAL DEVELOPMENT SETUP**

### **Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your database settings (DATABASE_URL, SECRET_KEY, etc.)

# Setup database (choose one option)
# Option 1: Local PostgreSQL
createdb property_mgmt
# Option 2: Docker PostgreSQL
docker run -d --name pms-postgres -p 5432:5432 \
  -e POSTGRES_DB=property_mgmt \
  -e POSTGRES_USER=property_user \
  -e POSTGRES_PASSWORD=secure_password \
  postgres:15-alpine

# Run migrations
python manage.py migrate
python manage.py create_demo_data

# Optional: Start Celery worker in another terminal
celery -A config worker --loglevel=info

# Start development server
python manage.py runserver 0.0.0.0:8000
```

### **Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env with API URL: VITE_API_URL=http://localhost:8000/api

# Optional: Install additional dev tools
npm install -g @types/node typescript

# Start development server (with hot reload)
npm run dev

# Access at: http://localhost:5173
```

---

## 🔧 **DEVELOPMENT WORKFLOW**

### **Code Quality Commands**
```bash
# Format all code
make format

# Lint all code
make lint

# Run all quality checks
make quality

# Run tests
make test
```

### **Git Workflow**
```bash
# Pre-commit hooks will automatically format and lint
git add .
git commit -m "feat: add new feature"
git push
```

---

## 🐳 **COMPREHENSIVE DOCKER GUIDE**

### **Development Environment**
```bash
# Start all services (recommended for development)
docker-compose up -d

# Start with Celery background tasks
docker-compose --profile celery up -d

# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### **Container Management**
```bash
# Check service status
docker-compose ps

# Restart specific service
docker-compose restart backend
docker-compose restart frontend

# Rebuild after code changes
docker-compose up -d --build backend
docker-compose up -d --build frontend

# Rebuild all services
docker-compose up -d --build
```

### **Database Operations**
```bash
# Access database shell
docker-compose exec db psql -U property_user -d property_mgmt

# Run Django migrations
docker-compose exec backend python manage.py migrate

# Create/load demo data
docker-compose exec backend python manage.py create_demo_data

# Reset database (WARNING: destroys all data)
docker-compose down -v
docker-compose up -d db
```

### **Development Workflow**
```bash
# Run backend commands
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py dbshell

# Run frontend commands
docker-compose exec frontend npm run build
docker-compose exec frontend npm run lint

# Check system health
curl http://localhost/health/
curl http://localhost/api/
```

### **Production Deployment**
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Setup SSL certificates
sudo certbot --nginx -d yourdomain.com

# View production logs
docker-compose -f docker-compose.prod.yml logs -f
```

### **Troubleshooting Docker**
```bash
# Clear Docker cache and rebuild
docker system prune -a
docker-compose build --no-cache

# Fix permission issues
sudo chown -R $USER:$USER .
sudo usermod -aG docker $USER

# Check resource usage
docker stats

# View container resource limits
docker-compose exec backend python manage.py check
```

---

## 🔐 **ENVIRONMENT CONFIGURATION**

### **Backend (.env)**
```bash
DEBUG=True
SECRET_KEY=your-development-secret-key
DATABASE_URL=postgresql://property_user:secure_password@localhost:5432/property_mgmt
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### **Frontend (.env)**
```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Property Management System
VITE_APP_VERSION=1.0.0
```

---

## 🧪 **TESTING**

### **Backend Tests**
```bash
cd backend
python manage.py test
```

### **Frontend Tests**
```bash
cd frontend
npm run test:run
```

---

## 🚀 **PRODUCTION DEPLOYMENT**

### **Quick Production Setup**
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Setup SSL (optional)
sudo certbot --nginx -d yourdomain.com
```

---

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

**Port already in use:**
```bash
# Find process using port
lsof -i :8000
lsof -i :5173

# Kill process
kill -9 <PID>
```

**Database connection issues:**
```bash
# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U property_user -d property_mgmt -c "SELECT 1;"
```

**Permission issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

---

## 📞 **NEED HELP?**

- **README.md**: Comprehensive project overview
- **DEVELOPER_GUIDE.md**: Detailed technical documentation
- **GitHub Issues**: Bug reports and feature requests
- **Docker Logs**: `docker-compose logs` for debugging

---

**Happy coding! 🎉**