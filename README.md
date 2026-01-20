# Property Management System (PMS)

A comprehensive full-stack property management application built with Django REST Framework and React/TypeScript.

## 🚀 Features

- **Property Management**: Track properties, occupancy rates, and financial data
- **Tenant Management**: Complete tenant profiles with lease information
- **Lease Management**: Lease agreements, renewals, and status tracking
- **Maintenance Requests**: Work order management with vendor assignment
- **Payment Processing**: Rent collection and financial transaction tracking
- **Accounting**: Financial reporting and expense management
- **User Management**: Role-based access control (Admin, Manager, Owner, Tenant)
- **Responsive UI**: Modern React interface with TypeScript

## 🛠️ Tech Stack

### Backend
- **Django 4.2+** with Django REST Framework
- **PostgreSQL 15** database
- **JWT Authentication** with refresh tokens
- **Redis** for caching
- **Gunicorn** WSGI server

### Frontend
- **React 19** with TypeScript
- **Vite** for fast development and building
- **Axios** for API communication
- **React Router** for navigation
- **Custom CSS** with CSS variables

### DevOps
- **Docker & Docker Compose** for containerization
- **Nginx** reverse proxy
- **PostgreSQL** database
- **Redis** caching

## 📋 Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

## 🚀 Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd property-management-system
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:8000/api
   - **Admin Panel**: http://localhost:8000/admin

4. **Demo Credentials**
   - **Admin**: `admin` / `admin123`
   - **Owner**: `owner` / `owner123`

## 🏃‍♂️ Local Development Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
python manage.py migrate
python manage.py create_demo_data
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env  # Configure your environment variables
npm run dev
```

## 📁 Project Structure

```
property-management-system/
├── backend/                 # Django backend
│   ├── apps/               # Django apps
│   │   ├── users/         # User management
│   │   ├── properties/    # Property management
│   │   ├── tenants/       # Tenant management
│   │   ├── leases/        # Lease management
│   │   ├── maintenance/   # Maintenance requests
│   │   ├── payments/      # Payment processing
│   │   └── accounting/    # Financial tracking
│   ├── config/            # Django settings
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Backend container
├── frontend/               # React frontend
│   ├── src/
│   │   ├── api/           # API client and endpoints
│   │   ├── components/    # Reusable React components
│   │   ├── context/       # React context providers
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Page components
│   │   ├── types/         # TypeScript interfaces
│   │   └── styles/        # CSS stylesheets
│   ├── package.json       # Node dependencies
│   └── Dockerfile         # Frontend container
├── docker-compose.yml      # Docker services
├── docker-compose.override.yml  # Development overrides
├── nginx.conf             # Nginx configuration
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

Create `.env` files in both `backend/` and `frontend/` directories:

**Backend (.env)**
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://property_user:secure_password@localhost:5432/property_mgmt
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
REDIS_URL=redis://localhost:6379/0
```

**Frontend (.env)**
```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Property Management System
VITE_APP_VERSION=1.0.0
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Run Django management commands
docker-compose exec backend python manage.py [command]

# Access database
docker-compose exec db psql -U property_user -d property_mgmt
```

## 🔐 Authentication & Permissions

### User Roles
- **Admin**: Full system access
- **Manager**: Property management access
- **Owner**: Own properties access
- **Tenant**: Limited access to own data

### API Authentication
- JWT tokens with refresh mechanism
- Automatic token refresh on expiration
- Secure logout with token blacklisting

## 📊 API Endpoints

### Authentication
- `POST /api/token/` - Login
- `POST /api/token/refresh/` - Refresh token
- `POST /api/users/register/` - Register

### Core Resources
- `GET/POST /api/properties/` - Property management
- `GET/POST /api/tenants/` - Tenant management
- `GET/POST /api/leases/` - Lease management
- `GET/POST /api/maintenance/` - Maintenance requests
- `GET/POST /api/payments/` - Payment processing

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🚀 Production Deployment

### Using Docker Compose
```bash
# Production setup
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With SSL/TLS
# Configure SSL certificates in nginx.conf
```

### Manual Deployment
1. Set up PostgreSQL database
2. Configure environment variables
3. Run migrations and collect static files
4. Set up Gunicorn and Nginx
5. Configure SSL certificates

## 🔄 Backup & Recovery

### Database Backup
```bash
# Using Docker
docker-compose exec db pg_dump -U property_user property_mgmt > backup.sql

# Manual backup
pg_dump -U property_user -d property_mgmt > backup.sql
```

### Database Restore
```bash
# Using Docker
docker-compose exec -T db psql -U property_user -d property_mgmt < backup.sql

# Manual restore
psql -U property_user -d property_mgmt < backup.sql
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the troubleshooting guide

---

**Built with ❤️ using Django, React, and Docker**