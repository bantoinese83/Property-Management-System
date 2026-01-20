# Property Management System - Quality Assurance

.PHONY: help format lint test quality clean

help: ## Show this help message
	@echo "Property Management System - Quality Assurance Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

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

# Development workflow
setup: install pre-commit-install ## Initial development setup

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

dev-backend: ## Start backend development server
	cd backend && python manage.py runserver

dev: ## Start both frontend and backend in development
	@echo "Starting development servers..."
	@echo "Frontend: http://localhost:5173"
	@echo "Backend: http://localhost:8000"
	@echo "Press Ctrl+C to stop all servers"
	make dev-backend & make dev-frontend & wait