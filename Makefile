# Property Management System - Development Workflow

.PHONY: help setup dev prod-deploy health backup restore

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "🚀 Property Management System - Development Commands"
	@echo ""
	@echo "📦 SETUP & INSTALLATION"
	@grep -E '^(setup|install|env-setup|pre-commit-install):.*## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🏗️  DEVELOPMENT"
	@grep -E '^(dev|dev-frontend|dev-backend|docker-up|docker-build):.*## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🧪 QUALITY ASSURANCE"
	@grep -E '^(quality|lint|format|test|type-check):.*## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🐳 DOCKER OPERATIONS"
	@grep -E '^docker-.*:.*## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🗄️  DATABASE"
	@grep -E '^(migrate|makemigrations|createsuperuser|backup|restore):.*## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔧 MAINTENANCE"
	@grep -E '^(health|clean|logs|status):.*## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📋 QUICK COMMANDS"
	@echo "  \033[36mmake setup\033[0m              - Complete development setup"
	@echo "  \033[36mmake dev\033[0m                - Start all development servers"
	@echo "  \033[36mmake quality\033[0m            - Run all quality checks (100/100)"
	@echo "  \033[36mmake docker-up\033[0m          - Start production containers"
	@echo "  \033[36mmake health\033[0m             - Check system health"
	@echo ""
	@echo "📚 For more information, see README.md"

# Frontend commands
format-frontend: ## Format frontend code with Prettier
	cd frontend && npm run format

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

lint-frontend-fix: ## Lint and fix frontend code
	cd frontend && npm run lint:fix

test-frontend: ## Run frontend tests
	cd frontend && npm run test:run

type-check-frontend: ## Run TypeScript type checking
	cd frontend && npm run type-check

quality-frontend: ## Run all frontend quality checks
	cd frontend && npm run quality

# Backend commands
format-backend: ## Format backend code with Black and isort
	cd backend && black .
	cd backend && isort .

lint-backend: ## Lint backend code with flake8
	cd backend && flake8 .

type-check-backend: ## Run mypy type checking
	cd backend && mypy .

test-backend: ## Run backend tests
	cd backend && python manage.py test

quality-backend: ## Run all backend quality checks
	cd backend && black --check . && isort --check-only . && flake8 . && mypy .

# Combined commands
format: format-frontend format-backend ## Format all code

lint: lint-frontend lint-backend ## Lint all code

test: test-frontend test-backend ## Run all tests

type-check: type-check-frontend type-check-backend ## Run all type checking

quality: quality-frontend quality-backend ## Run all quality checks (100/100 score)

# Development setup
install-frontend: ## Install frontend dependencies
	cd frontend && npm install

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install: install-frontend install-backend ## Install all dependencies

# Pre-commit setup
pre-commit-install: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files

# Docker commands
docker-build: ## Build Docker containers
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-celery: ## Start Celery worker
	docker-compose --profile celery up -d celery

docker-celery-logs: ## Show Celery logs
	docker-compose logs -f celery

# Database commands
migrate: ## Run Django migrations
	cd backend && python manage.py migrate

makemigrations: ## Create Django migrations
	cd backend && python manage.py makemigrations

createsuperuser: ## Create Django superuser
	cd backend && python manage.py createsuperuser

# Cleanup
clean-frontend: ## Clean frontend build artifacts
	cd frontend && rm -rf node_modules dist

clean-backend: ## Clean backend cache and artifacts
	cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	cd backend && find . -type f -name "*.pyc" -delete
	cd backend && find . -type f -name "*.pyo" -delete
	cd backend && find . -type f -name "*.pyd" -delete

clean: clean-frontend clean-backend ## Clean all artifacts

# Environment setup
env-setup: ## Copy environment example file
	cp env.example .env
	@echo "Environment file created. Please edit .env with your actual values."

# Development workflow
setup: install pre-commit-install env-setup ## Complete development setup (recommended)
dev: docker-up docker-celery ## Start full development environment with Docker
dev-local: ## Start local development (backend + frontend)
	@echo "🚀 Starting local development servers..."
	@echo "📊 Frontend: http://localhost:5173"
	@echo "🔧 Backend: http://localhost:8000"
	@echo "📋 API Docs: http://localhost:8000/docs"
	@echo "👑 Admin: http://localhost:8000/admin"
	@echo "Press Ctrl+C to stop all servers"
	$(MAKE) dev-backend & $(MAKE) dev-frontend & wait

dev-frontend: ## Start frontend development server
	@echo "🎨 Starting frontend development server..."
	cd frontend && npm run dev

dev-backend: ## Start backend development server
	@echo "🔧 Starting backend development server..."
	cd backend && python manage.py runserver 0.0.0.0:8000

dev-debug: ## Start services with debug logging
	@echo "🐛 Starting services with debug logging..."
	DJANGO_LOG_LEVEL=DEBUG $(MAKE) dev-local

# Production deployment
prod-deploy: ## Deploy to production (requires proper environment setup)
	@echo "🚀 Deploying to production..."
	docker-compose -f docker-compose.prod.yml down || true
	docker-compose -f docker-compose.prod.yml build --no-cache
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production deployment complete!"
	@echo "🌐 Application available at your configured domain"

# Health and monitoring
health: ## Check system health and status
	@echo "🏥 Checking system health..."
	@if command -v docker-compose >/dev/null 2>&1; then \
		echo "🐳 Docker containers:"; \
		docker-compose ps; \
		echo ""; \
		echo "📊 Health check:"; \
		curl -s http://localhost/health/ | python3 -m json.tool || echo "❌ Health check failed"; \
	else \
		echo "❌ Docker not available"; \
	fi

status: ## Show detailed system status
	@echo "📊 System Status Report"
	@echo "======================"
	@echo "🐳 Docker containers:"
	@docker-compose ps
	@echo ""
	@echo "💾 Disk usage:"
	@df -h | head -n 5
	@echo ""
	@echo "🧠 Memory usage:"
	@free -h 2>/dev/null || echo "free command not available"
	@echo ""
	@echo "🔥 Running processes:"
	@ps aux --no-headers | wc -l | xargs echo "Total processes:"

logs: ## Show all application logs
	docker-compose logs -f --tail=100

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

logs-db: ## Show database logs
	docker-compose logs -f db

# Backup and restore
backup: ## Create full system backup
	@echo "💾 Creating system backup..."
	@mkdir -p backups
	@echo "📁 Backing up media files..."
	@docker cp $$(docker-compose ps -q backend):/code/media ./backups/media_$$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "⚠️  Media backup failed"
	@echo "🗄️  Backing up database..."
	@docker-compose exec -T db pg_dump -U property_user property_mgmt > ./backups/db_$$(date +%Y%m%d_%H%M%S).sql 2>/dev/null || echo "⚠️  Database backup failed"
	@echo "✅ Backup complete: ./backups/"

restore: ## Restore from backup (specify BACKUP_DATE)
	@echo "🔄 Restoring from backup..."
	@if [ -z "$(BACKUP_DATE)" ]; then \
		echo "❌ Please specify BACKUP_DATE=YYYYMMDD_HHMMSS"; \
		exit 1; \
	fi
	@echo "📁 Restoring media files..."
	@docker cp ./backups/media_$(BACKUP_DATE) $$(docker-compose ps -q backend):/code/media 2>/dev/null || echo "⚠️  Media restore failed"
	@echo "🗄️  Restoring database..."
	@docker-compose exec -T db psql -U property_user property_mgmt < ./backups/db_$(BACKUP_DATE).sql 2>/dev/null || echo "⚠️  Database restore failed"
	@echo "✅ Restore complete!"

# Performance monitoring
perf-frontend: ## Analyze frontend bundle performance
	cd frontend && npm run build:analyze

perf-backend: ## Analyze backend query performance
	@echo "🔍 Analyzing database query performance..."
	docker-compose exec backend python manage.py shell -c "
	from core.db_utils import analyze_table_performance
	from properties.models import Property
	from tenants.models import Tenant
	from leases.models import Lease

	print('📊 Property table analysis:')
	print(analyze_table_performance(Property))
	print()
	print('📊 Tenant table analysis:')
	print(analyze_table_performance(Tenant))
	print()
	print('📊 Lease table analysis:')
	print(analyze_table_performance(Lease))
	"

# Security checks
security-scan: ## Run security vulnerability scans
	@echo "🔒 Running security scans..."
	@echo "📦 Frontend dependencies:"
	@cd frontend && npm audit --audit-level moderate || echo "⚠️  Frontend security issues found"
	@echo "🐍 Backend dependencies:"
	@cd backend && python -m pip_audit --format json || echo "⚠️  pip-audit not installed"
	@echo "🔍 Django security check:"
	@cd backend && python manage.py check --deploy || echo "⚠️  Django security issues found"

# Documentation
docs-build: ## Build documentation
	@echo "📚 Building documentation..."
	@echo "🔧 API documentation available at: http://localhost:8000/docs"
	@echo "📖 Frontend docs: cd frontend && npm run docs"

docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@echo "🔧 API Docs: http://localhost:8000/docs"
	@echo "📖 Frontend: cd frontend && npm run docs"

# Utility commands
shell-backend: ## Open Django shell
	docker-compose exec backend python manage.py shell

shell-db: ## Open database shell
	docker-compose exec db psql -U property_user property_mgmt

format-fix: ## Auto-fix formatting issues
	@echo "🔧 Auto-fixing formatting issues..."
	$(MAKE) lint-frontend-fix
	$(MAKE) format-backend

deps-update: ## Update all dependencies
	@echo "📦 Updating dependencies..."
	cd frontend && npm update
	cd backend && pip install --upgrade -r requirements.txt

deps-check: ## Check for outdated dependencies
	@echo "📦 Checking for outdated dependencies..."
	cd frontend && npm run deps:check
	@echo "🐍 Backend dependencies:"
	cd backend && python -m pip list --outdated --format json