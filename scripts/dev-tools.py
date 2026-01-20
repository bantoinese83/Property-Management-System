#!/usr/bin/env python
"""
Developer Tools for Property Management System

This script provides various development utilities to make working
on the PMS project more efficient and enjoyable.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection


class DevTools:
    """Collection of developer utilities."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"

    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a shell command and return the result."""
        try:
            return subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(command)}")
            print(f"Error: {e.stderr}")
            raise

    def check_services_health(self) -> Dict[str, Any]:
        """Check the health of all services."""
        print("🔍 Checking service health...")

        health_status = {
            "services": {},
            "issues": []
        }

        # Check Docker services
        try:
            result = self.run_command(["docker-compose", "ps"])
            services = ["backend", "frontend", "db", "redis", "nginx"]
            for service in services:
                if service in result.stdout:
                    health_status["services"][service] = "running"
                else:
                    health_status["services"][service] = "stopped"
                    health_status["issues"].append(f"{service} service is not running")
        except Exception as e:
            health_status["issues"].append(f"Failed to check Docker services: {e}")

        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_status["services"]["database"] = "connected"
        except Exception as e:
            health_status["services"]["database"] = "disconnected"
            health_status["issues"].append(f"Database connection failed: {e}")

        return health_status

    def reset_database(self, confirm: bool = False) -> None:
        """Reset the database with fresh data."""
        if not confirm:
            response = input("⚠️  This will delete all data. Continue? (yes/no): ")
            if response.lower() != "yes":
                print("Operation cancelled.")
                return

        print("🔄 Resetting database...")

        # Stop services
        self.run_command(["docker-compose", "down"])

        # Remove volumes and recreate
        self.run_command(["docker-compose", "down", "-v"])
        self.run_command(["docker-compose", "up", "-d", "db"])

        # Wait for database to be ready
        print("⏳ Waiting for database to be ready...")
        import time
        time.sleep(10)

        # Run migrations and create demo data
        self.run_command(["docker-compose", "exec", "backend", "python", "manage.py", "migrate"])
        self.run_command(["docker-compose", "exec", "backend", "python", "manage.py", "create_demo_data"])

        # Start all services
        self.run_command(["docker-compose", "up", "-d"])

        print("✅ Database reset complete!")

    def run_quality_checks(self) -> Dict[str, Any]:
        """Run all code quality checks."""
        print("🔍 Running quality checks...")

        results = {
            "backend": {},
            "frontend": {},
            "overall": "passed"
        }

        # Backend checks
        try:
            # Run black check
            self.run_command(["black", "--check", "--diff", "backend"], cwd=self.backend_dir)
            results["backend"]["formatting"] = "passed"
        except:
            results["backend"]["formatting"] = "failed"

        try:
            # Run isort check
            self.run_command(["isort", "--check-only", "--diff", "backend"], cwd=self.backend_dir)
            results["backend"]["imports"] = "passed"
        except:
            results["backend"]["imports"] = "failed"

        try:
            # Run flake8
            self.run_command(["flake8", "backend"], cwd=self.backend_dir)
            results["backend"]["linting"] = "passed"
        except:
            results["backend"]["linting"] = "failed"

        try:
            # Run mypy
            self.run_command(["mypy", "backend"], cwd=self.backend_dir)
            results["backend"]["types"] = "passed"
        except:
            results["backend"]["types"] = "failed"

        # Frontend checks
        try:
            # Run ESLint
            self.run_command(["npm", "run", "lint"], cwd=self.frontend_dir)
            results["frontend"]["linting"] = "passed"
        except:
            results["frontend"]["linting"] = "failed"

        try:
            # Run TypeScript check
            self.run_command(["npm", "run", "type-check"], cwd=self.frontend_dir)
            results["frontend"]["types"] = "passed"
        except:
            results["frontend"]["types"] = "failed"

        # Determine overall status
        all_checks = []
        for category in ["backend", "frontend"]:
            for check, status in results[category].items():
                all_checks.append(status)

        if "failed" in all_checks:
            results["overall"] = "failed"

        return results

    def fix_code_quality(self) -> None:
        """Automatically fix code quality issues."""
        print("🔧 Fixing code quality issues...")

        # Backend fixes
        print("Backend fixes:")
        try:
            self.run_command(["black", "backend"], cwd=self.backend_dir)
            print("✅ Formatting fixed")
        except Exception as e:
            print(f"❌ Formatting fix failed: {e}")

        try:
            self.run_command(["isort", "backend"], cwd=self.backend_dir)
            print("✅ Import sorting fixed")
        except Exception as e:
            print(f"❌ Import sorting failed: {e}")

        # Frontend fixes
        print("Frontend fixes:")
        try:
            self.run_command(["npm", "run", "lint:fix"], cwd=self.frontend_dir)
            print("✅ Linting issues fixed")
        except Exception as e:
            print(f"❌ Linting fix failed: {e}")

    def generate_api_docs(self) -> None:
        """Generate API documentation."""
        print("📚 Generating API documentation...")

        try:
            # This would integrate with drf-spectacular or similar
            self.run_command(["docker-compose", "exec", "backend", "python", "manage.py", "spectacular", "--file", "api-schema.yml"])
            print("✅ API schema generated")
        except Exception as e:
            print(f"⚠️  API documentation generation failed: {e}")
            print("Note: Install drf-spectacular for full API docs")

    def show_database_stats(self) -> Dict[str, Any]:
        """Show database statistics."""
        print("📊 Database statistics:")

        try:
            with connection.cursor() as cursor:
                # Get table counts
                cursor.execute("""
                    SELECT table_name, (SELECT n_tup_ins - n_tup_del FROM pg_stat_user_tables WHERE relname = table_name) as row_count
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)

                tables = {row[0]: row[1] for row in cursor.fetchall()}

                # Get database size
                cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
                db_size = cursor.fetchone()[0]

                stats = {
                    "database_size": db_size,
                    "tables": tables,
                    "total_tables": len(tables),
                    "total_records": sum(tables.values())
                }

                print(f"Database size: {db_size}")
                print(f"Total tables: {len(tables)}")
                print(f"Total records: {sum(tables.values())}")

                for table, count in tables.items():
                    print(f"  {table}: {count} records")

                return stats

        except Exception as e:
            print(f"❌ Failed to get database stats: {e}")
            return {}

    def create_test_user(self, username: str = "testuser", email: str = "test@example.com") -> None:
        """Create a test user for development."""
        from django.contrib.auth import get_user_model
        from django.core.management import call_command

        User = get_user_model()

        try:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="testpass123",
                    user_type="owner",
                    first_name="Test",
                    last_name="User"
                )
                print(f"✅ Test user created: {username}")
                print(f"   Email: {email}")
                print(f"   Password: testpass123")
            else:
                print(f"⚠️  Test user {username} already exists")
        except Exception as e:
            print(f"❌ Failed to create test user: {e}")

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run basic performance tests."""
        print("⚡ Running performance tests...")

        import time

        results = {}

        # API response time test
        try:
            start_time = time.time()
            result = self.run_command([
                "curl", "-s", "-w", "%{time_total}",
                "http://localhost/api/properties/"
            ])
            response_time = float(result.stdout.strip())
            results["api_response_time"] = f"{response_time:.3f}s"
            print(".3f"        except:
            results["api_response_time"] = "failed"

        # Database query performance
        try:
            with connection.cursor() as cursor:
                start_time = time.time()
                cursor.execute("SELECT COUNT(*) FROM properties_property")
                count = cursor.fetchone()[0]
                query_time = time.time() - start_time
                results["db_query_time"] = f"{query_time:.4f}s"
                results["property_count"] = count
                print(".4f"        except:
            results["db_query_time"] = "failed"

        return results


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Developer Tools for Property Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/dev-tools.py health          # Check service health
  python scripts/dev-tools.py reset-db --yes  # Reset database
  python scripts/dev-tools.py quality         # Run quality checks
  python scripts/dev-tools.py fix             # Auto-fix quality issues
  python scripts/dev-tools.py db-stats        # Show database stats
  python scripts/dev-tools.py create-test-user # Create test user
  python scripts/dev-tools.py perf-test       # Run performance tests
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Health check
    subparsers.add_parser("health", help="Check service health")

    # Database reset
    reset_parser = subparsers.add_parser("reset-db", help="Reset database with fresh data")
    reset_parser.add_argument("--yes", action="store_true", help="Skip confirmation")

    # Quality checks
    subparsers.add_parser("quality", help="Run all code quality checks")
    subparsers.add_parser("fix", help="Auto-fix code quality issues")

    # Documentation
    subparsers.add_parser("api-docs", help="Generate API documentation")

    # Database stats
    subparsers.add_parser("db-stats", help="Show database statistics")

    # Test user
    subparsers.add_parser("create-test-user", help="Create a test user")

    # Performance tests
    subparsers.add_parser("perf-test", help="Run performance tests")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    tools = DevTools()

    try:
        if args.command == "health":
            health = tools.check_services_health()
            print("\n📋 Health Status:")
            for service, status in health["services"].items():
                status_icon = "✅" if status in ["running", "connected"] else "❌"
                print(f"  {status_icon} {service}: {status}")

            if health["issues"]:
                print("\n⚠️  Issues found:")
                for issue in health["issues"]:
                    print(f"  • {issue}")

        elif args.command == "reset-db":
            tools.reset_database(confirm=args.yes)

        elif args.command == "quality":
            results = tools.run_quality_checks()
            print("
📋 Quality Check Results:"            for category in ["backend", "frontend"]:
                print(f"\n{category.title()}:")
                for check, status in results[category].items():
                    status_icon = "✅" if status == "passed" else "❌"
                    print(f"  {status_icon} {check}: {status}")

            overall_status = results["overall"]
            status_icon = "✅" if overall_status == "passed" else "❌"
            print(f"\n{status_icon} Overall: {overall_status}")

        elif args.command == "fix":
            tools.fix_code_quality()
            print("✅ Code quality fixes applied!")

        elif args.command == "api-docs":
            tools.generate_api_docs()

        elif args.command == "db-stats":
            tools.show_database_stats()

        elif args.command == "create-test-user":
            tools.create_test_user()

        elif args.command == "perf-test":
            results = tools.run_performance_tests()
            print("\n📊 Performance Results:")
            for metric, value in results.items():
                print(f"  • {metric}: {value}")

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()