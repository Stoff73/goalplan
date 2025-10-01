# Database Setup Guide

## Overview

GoalPlan uses **PostgreSQL** for relational data storage and **Redis** for caching and session management. This guide covers the setup and configuration of both services for local development.

## Table of Contents

1. [PostgreSQL Setup](#postgresql-setup)
2. [Redis Setup](#redis-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Migrations](#database-migrations)
5. [Testing Database Connectivity](#testing-database-connectivity)
6. [Troubleshooting](#troubleshooting)

---

## PostgreSQL Setup

### Installation

#### macOS (using Homebrew)
```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Verify installation
psql --version
```

#### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

#### Windows
1. Download PostgreSQL installer from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run installer and follow setup wizard
3. Remember the superuser password you set during installation

### Database and User Creation

```bash
# Connect to PostgreSQL as superuser
psql postgres

# Create database user
CREATE USER goalplan_user WITH PASSWORD 'goalplan_dev_password';

# Create development database
CREATE DATABASE goalplan_dev OWNER goalplan_user;

# Create test database (optional but recommended)
CREATE DATABASE goalplan_test OWNER goalplan_user;

# Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE goalplan_dev TO goalplan_user;
GRANT ALL PRIVILEGES ON DATABASE goalplan_test TO goalplan_user;

# Exit psql
\q
```

### Test PostgreSQL Connection

```bash
# Test connection with created user
psql -U goalplan_user -d goalplan_dev -h localhost

# You should see the psql prompt
goalplan_dev=>

# Test a simple query
SELECT version();

# Exit
\q
```

---

## Redis Setup

### Installation

#### macOS (using Homebrew)
```bash
# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Verify installation
redis-cli --version
```

#### Ubuntu/Debian
```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify installation
redis-cli --version
```

#### Windows
1. Download Redis for Windows from [GitHub releases](https://github.com/tporadowski/redis/releases)
2. Extract and run `redis-server.exe`
3. Optionally install as Windows service

### Test Redis Connection

```bash
# Connect to Redis
redis-cli

# Test with PING command (should return PONG)
127.0.0.1:6379> PING
PONG

# Set and get a test value
127.0.0.1:6379> SET test "Hello Redis"
OK
127.0.0.1:6379> GET test
"Hello Redis"

# Exit
127.0.0.1:6379> EXIT
```

---

## Environment Configuration

### Create .env File

1. Copy the example environment file:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Edit `.env` file with your local configuration:
   ```bash
   # Use your preferred text editor
   nano .env
   # or
   code .env
   ```

3. Update the following critical settings:

   ```env
   # Database Configuration
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   DATABASE_USER=goalplan_user
   DATABASE_PASSWORD=your_secure_password_here
   DATABASE_NAME=goalplan_dev

   # Redis Configuration
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=
   REDIS_DB=0

   # Security Settings
   JWT_SECRET_KEY=your_generated_secret_key_here
   ```

### Generate Secure Keys

```bash
# Generate JWT secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate encryption key for sensitive data
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the generated keys to your `.env` file.

---

## Database Migrations

### Alembic Configuration

Alembic is configured and ready to use for database migrations.

### Common Alembic Commands

```bash
# Initialize database with migrations (first time only)
cd backend
alembic upgrade head

# Create a new migration (auto-generate from model changes)
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# View current migration version
alembic current
```

### Creating Your First Migration

```bash
# After creating your first model (e.g., User model)
cd backend
alembic revision --autogenerate -m "Create user table"

# Review the generated migration in alembic/versions/
# Then apply it
alembic upgrade head
```

---

## Testing Database Connectivity

### Run Connectivity Tests

The project includes comprehensive connectivity tests for both PostgreSQL and Redis.

```bash
# From the backend directory
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run all connectivity tests
pytest tests/test_connectivity.py -v

# Run specific test classes
pytest tests/test_connectivity.py::TestDatabaseConnectivity -v
pytest tests/test_connectivity.py::TestRedisConnectivity -v

# Run with coverage
pytest tests/test_connectivity.py --cov=backend --cov-report=html
```

### Expected Test Output

```
tests/test_connectivity.py::TestDatabaseConnectivity::test_database_connection PASSED
tests/test_connectivity.py::TestDatabaseConnectivity::test_database_connection_check PASSED
tests/test_connectivity.py::TestRedisConnectivity::test_redis_connection PASSED
tests/test_connectivity.py::TestRedisConnectivity::test_redis_set_get PASSED
tests/test_connectivity.py::TestRedisConnectivity::test_redis_set_get_json PASSED
...

================================ X passed in Y.YYs ================================
```

### Manual Connectivity Check

You can also test connectivity programmatically:

```python
# test_connection.py
import asyncio
from backend.database import check_db_connection
from backend.redis_client import redis_client

async def main():
    # Test database
    db_connected = await check_db_connection()
    print(f"Database connected: {db_connected}")

    # Test Redis
    await redis_client.connect()
    redis_connected = await redis_client.check_connection()
    print(f"Redis connected: {redis_connected}")
    await redis_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

Run with:
```bash
python test_connection.py
```

---

## Troubleshooting

### PostgreSQL Issues

#### "psql: error: connection to server on socket failed"

**Solution:**
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux

# Start PostgreSQL if not running
brew services start postgresql@15     # macOS
sudo systemctl start postgresql       # Linux
```

#### "FATAL: password authentication failed for user"

**Solution:**
1. Reset password:
   ```bash
   sudo -u postgres psql
   ALTER USER goalplan_user WITH PASSWORD 'new_password';
   ```
2. Update `.env` file with new password

#### "FATAL: database does not exist"

**Solution:**
```bash
# Create the database
createdb -U goalplan_user goalplan_dev

# Or using psql
psql -U postgres
CREATE DATABASE goalplan_dev OWNER goalplan_user;
```

### Redis Issues

#### "Could not connect to Redis at 127.0.0.1:6379: Connection refused"

**Solution:**
```bash
# Check if Redis is running
brew services list | grep redis       # macOS
sudo systemctl status redis-server    # Linux

# Start Redis if not running
brew services start redis             # macOS
sudo systemctl start redis-server     # Linux
```

#### "NOAUTH Authentication required"

**Solution:**
1. If Redis has a password, update `.env`:
   ```env
   REDIS_PASSWORD=your_redis_password
   ```
2. Or remove password from Redis config (`/usr/local/etc/redis.conf`)

### Alembic Issues

#### "Can't locate revision identified by"

**Solution:**
```bash
# Reset alembic version table
alembic stamp head

# Or drop and recreate
psql -U goalplan_user -d goalplan_dev
DROP TABLE alembic_version;
\q

# Re-run migrations
alembic upgrade head
```

#### "Target database is not up to date"

**Solution:**
```bash
# Apply all pending migrations
alembic upgrade head
```

---

## Configuration Files Reference

### Database Configuration Files

| File | Purpose |
|------|---------|
| `backend/config.py` | Centralized configuration management |
| `backend/database.py` | SQLAlchemy database connection setup |
| `backend/redis_client.py` | Redis client and session management |
| `backend/.env` | Environment variables (local only) |
| `backend/.env.example` | Environment variables template |
| `backend/alembic.ini` | Alembic migration configuration |
| `backend/alembic/env.py` | Alembic environment setup |

### Important Notes

1. **Never commit `.env` file to version control**
   - It contains sensitive credentials
   - Use `.env.example` as template

2. **Use strong passwords in production**
   - Generate random passwords
   - Store in secure secret management system

3. **Enable SSL/TLS in production**
   - PostgreSQL: Update connection string with `sslmode=require`
   - Redis: Use `rediss://` protocol

4. **Database backups**
   - Set up automated backups
   - Test restore procedures regularly

5. **Connection pooling**
   - Adjust pool sizes based on load
   - Monitor connection usage

---

## Next Steps

Once database setup is complete:

1. ✅ Verify all tests pass: `pytest tests/test_connectivity.py -v`
2. ✅ Create your first model in `backend/models/`
3. ✅ Generate migration: `alembic revision --autogenerate -m "description"`
4. ✅ Apply migration: `alembic upgrade head`
5. ✅ Proceed to Phase 1 development (Authentication)

---

## Support and Resources

- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **Redis Documentation:** https://redis.io/documentation
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/
- **Alembic Documentation:** https://alembic.sqlalchemy.org/
- **FastAPI Database Guide:** https://fastapi.tiangolo.com/tutorial/sql-databases/

For project-specific issues, refer to:
- `CLAUDE.md` - Project overview and guidelines
- `Architecture.md` - System architecture
- `DataManagement.md` - Data handling requirements
- `securityCompliance.md` - Security requirements
