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
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

### **5. Demo Credentials**
- **Admin**: `admin` / `admin123`
- **Owner**: `owner` / `owner123`

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
# Edit .env with your database settings

# Setup database
createdb property_mgmt  # Or use Docker: docker-compose up -d db

# Run migrations
python manage.py migrate
python manage.py create_demo_data

# Start development server
python manage.py runserver
```

### **Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env with API URL: VITE_API_URL=http://localhost:8000/api

# Start development server
npm run dev
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

## 🐳 **DOCKER COMMANDS**

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Rebuild after code changes
docker-compose up -d --build

# Stop all services
docker-compose down

# Reset database (WARNING: destroys data)
docker-compose down -v
docker-compose up -d db
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