#!/usr/bin/env python3
"""
Database setup verification script.

This script verifies that all database configuration files are in place
and provides instructions for running the connectivity tests.

Run this script to check if the database setup is complete.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists and report status."""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists


def main():
    """Main verification function."""
    print("=" * 70)
    print("GoalPlan Database Setup Verification")
    print("=" * 70)
    print()

    backend_dir = Path(__file__).parent
    all_good = True

    print("1. Checking configuration files...")
    print("-" * 70)
    all_good &= check_file_exists(
        str(backend_dir / "config.py"),
        "Configuration module"
    )
    all_good &= check_file_exists(
        str(backend_dir / ".env.example"),
        "Environment template"
    )
    print()

    print("2. Checking database modules...")
    print("-" * 70)
    all_good &= check_file_exists(
        str(backend_dir / "database.py"),
        "Database connection module"
    )
    all_good &= check_file_exists(
        str(backend_dir / "redis_client.py"),
        "Redis client module"
    )
    print()

    print("3. Checking Alembic migration setup...")
    print("-" * 70)
    all_good &= check_file_exists(
        str(backend_dir / "alembic.ini"),
        "Alembic configuration"
    )
    all_good &= check_file_exists(
        str(backend_dir / "alembic" / "env.py"),
        "Alembic environment"
    )
    all_good &= check_file_exists(
        str(backend_dir / "alembic" / "script.py.mako"),
        "Alembic template"
    )
    all_good &= check_file_exists(
        str(backend_dir / "alembic" / "versions"),
        "Migration versions directory"
    )
    print()

    print("4. Checking test files...")
    print("-" * 70)
    all_good &= check_file_exists(
        str(backend_dir / "tests" / "conftest.py"),
        "Test configuration"
    )
    all_good &= check_file_exists(
        str(backend_dir / "tests" / "test_connectivity.py"),
        "Connectivity tests"
    )
    print()

    print("5. Checking documentation...")
    print("-" * 70)
    all_good &= check_file_exists(
        str(backend_dir / "DATABASE_SETUP.md"),
        "Database setup guide"
    )
    print()

    print("=" * 70)
    if all_good:
        print("✓ All database configuration files are in place!")
        print()
        print("Next steps:")
        print("-" * 70)
        print("1. Install dependencies:")
        print("   $ pip install -r requirements.txt")
        print()
        print("2. Set up PostgreSQL and Redis (see DATABASE_SETUP.md)")
        print()
        print("3. Create .env file from template:")
        print("   $ cp .env.example .env")
        print("   $ nano .env  # Edit with your configuration")
        print()
        print("4. Run connectivity tests:")
        print("   $ pytest tests/test_connectivity.py -v")
        print()
        print("5. Initialize database migrations:")
        print("   $ alembic upgrade head")
        print()
        print("For detailed instructions, see: DATABASE_SETUP.md")
    else:
        print("✗ Some files are missing. Please complete the setup.")
        return 1

    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
