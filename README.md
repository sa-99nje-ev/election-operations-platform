# Election Operations Platform

A production-oriented backend platform for managing election operations, built with **FastAPI**, **async Python**, **PostgreSQL**, **Redis**, and **SQLAlchemy 2.0**.

The platform provides secure election-domain management, role-based authentication, asynchronous vote processing, audit logging, database migrations, automated testing, performance testing, and containerized deployment.

---

## 🚀 Features

### Authentication & Authorization

- JWT-based authentication
- Role-based access control
- Supported roles:
  - Admin
  - Officer
  - Voter
  - Candidate
- Password hashing with Passlib + bcrypt
- JWT access/refresh token support
- Refresh-token persistence and invalidation

### Election Domain Management

- Constituency management
- Polling booth management
- Voter management
- Candidate management
- Voting record management
- Relational integrity enforced through PostgreSQL foreign keys

### Asynchronous Vote Processing

- ARQ background task processing
- Redis-backed task queue
- Non-blocking vote processing
- Idempotent vote requests using `request_id`
- Background processing separated from API request handling

### Audit & Security

- Security-critical operations recorded through audit logs
- Actor tracking
- Target tracking
- Operation outcome tracking
- IP address recording
- Database-level referential integrity

### Database

- PostgreSQL
- SQLAlchemy 2.0 async ORM
- `asyncpg` PostgreSQL driver
- Alembic migrations
- Version-controlled database schema
- Composite indexes for performance-critical queries
- Foreign-key constraints and uniqueness constraints

### Testing & Quality

- Pytest
- pytest-asyncio
- HTTPX
- pytest-cov
- Factory Boy
- Flake8
- Performance test suite
- Worker scaling tests
- Database persistence tests
- Vote pipeline tests
- Reliability/integrity tests

### CI/CD

GitHub Actions automatically validates:

- Code quality
- Test suite
- Coverage generation
- Docker build
- Docker Compose configuration

### Containerization

- Docker
- Docker Compose
- PostgreSQL service
- Redis service
- FastAPI application
- ARQ worker

---

# 🛠 Tech Stack

| Component | Technology |
|---|---|
| Backend Framework | FastAPI |
| Language | Python 3.10+ |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 15+ |
| Async PostgreSQL Driver | asyncpg |
| Async SQLite Testing | aiosqlite |
| Migrations | Alembic |
| Background Processing | ARQ |
| Message Broker | Redis |
| Authentication | JWT / python-jose |
| Password Hashing | Passlib + bcrypt |
| Validation | Pydantic 2 |
| API Testing | Pytest + HTTPX |
| Async Testing | pytest-asyncio |
| Test Data | Factory Boy |
| Coverage | pytest-cov |
| Load Testing | Locust |
| Code Quality | Flake8, Black, isort, mypy |
| Security Analysis | Bandit, pip-audit |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

# 🏗 Architecture

```text
                    ┌──────────────────────┐
                    │       Client         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI API     │
                    │                      │
                    │  Routers / Schemas   │
                    │  Authentication      │
                    │  Authorization       │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐       ┌──────────────────┐
       │   PostgreSQL     │       │      Redis       │
       │                  │       │                  │
       │ SQLAlchemy 2.0   │       │ ARQ Task Queue   │
       │ Election Data    │       │                  │
       └──────────────────┘       └────────┬─────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │    ARQ Worker    │
                                  │                  │
                                  │ Vote Processing  │
                                  └──────────────────┘
📁 Project Structure
election-operations-platform/
│
├── app/
│   ├── core/
│   │   ├── configuration/
│   │   ├── security.py
│   │   └── ...
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── constituency.py
│   │   ├── voter.py
│   │   ├── candidate.py
│   │   ├── polling_booth.py
│   │   ├── voting_record.py
│   │   ├── audit_log.py
│   │   └── refresh_token.py
│   │
│   ├── repositories/
│   │
│   ├── routers/
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │
│   ├── workers/
│   │
│   ├── arq_worker.py
│   │
│   ├── database.py
│   └── main.py
│
├── migrations/
│   ├── env.py
│   └── versions/
│       ├── 20577bf67e5c_initial_schema.py
│       ├── 002_performance_indexes.py
│       └── 917949da489c_migrate_to_fastapi_async.py
│
├── tests/
│   ├── performance/
│   │   ├── test_api_latency.py
│   │   ├── test_database.py
│   │   ├── test_reliability.py
│   │   ├── test_vote_pipeline.py
│   │   └── test_worker_scaling.py
│   │
│   ├── unit/
│   │   ├── test_services.py
│   │   └── test_worker.py
│   │
│   ├── test_api.py
│   ├── test_domain.py
│   └── conftest.py
│
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
└── README.md
🚀 Getting Started
Prerequisites

Install the following:

Python 3.10+
PostgreSQL 15+
Redis 7+
Git
Docker Desktop (optional, for containerized deployment)
1. Clone the Repository
git clone https://github.com/sa-99nje-ev/election-operations-platform.git
cd election-operations-platform
2. Create a Virtual Environment
Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
⚙️ Configuration

Create a .env file in the project root.

Example:

DATABASE_URL=postgresql+asyncpg://election_user:password@localhost:5432/election_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

Do not commit real secrets to Git.

🗄️ Database Setup

Make sure PostgreSQL is running and the configured database exists.

Then apply all Alembic migrations:

alembic upgrade head

Check the current migration:

alembic current

View the migration history:

alembic history

The final migration chain establishes the complete database schema and performance indexes.

▶️ Running the Application

Start the FastAPI server:

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

The API will be available at:

http://localhost:8000

Swagger UI:

http://localhost:8000/docs

ReDoc:

http://localhost:8000/redoc
⚙️ Running the ARQ Worker

Start the asynchronous vote-processing worker:

arq app.arq_worker.WorkerSettings

The worker consumes background tasks from Redis and performs asynchronous vote processing.

🧪 Testing

Run the complete test suite:

pytest tests/ -v --tb=short

Run performance tests:

pytest tests/performance/ -v

Run unit tests:

pytest tests/unit/ -v

Run coverage:

pytest --cov=app --cov-report=xml --cov-report=term-missing tests/
✅ Final Validation

The final project validation successfully achieved:

11 tests passed
Flake8 critical checks: 0 errors
Coverage report: generated
Docker build: successful
Docker Compose validation: successful
GitHub Actions CI: successful

The automated CI pipeline validates both the application and containerized deployment configuration.

🔍 Code Quality

Run the critical Flake8 checks:

flake8 app/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics

Run Git whitespace validation:

git diff --check

Optional formatting:

black app/ tests/
isort app/ tests/
📊 Performance & Load Testing

Run the performance test suite:

pytest tests/performance/ -v
The performance suite covers:

API latency
Database persistence
Election integrity
Vote submission pipeline
Worker scaling
System capacity under increasing workloads
🐳 Docker Deployment

Build and start all services:

docker compose up --build

Run in detached mode:

docker compose up -d --build

Stop services:

docker compose down

Rebuild without cache:

docker compose build --no-cache

Typical services include:

FastAPI       → localhost:8000
PostgreSQL    → localhost:5432
Redis         → localhost:6379
ARQ Worker
🔐 Security

The application incorporates several security mechanisms:

JWT authentication
Role-based authorization
Password hashing
Refresh-token management
Token invalidation
Database-level foreign-key constraints
Unique constraints
Audit logging
Rate limiting
Environment-based secret configuration
Dependency vulnerability auditing with pip-audit
Static security analysis with Bandit

Production deployments should use strong, externally managed secrets rather than the example values shown in this README.

🗳️ Vote Processing Flow
Client
  │
  │ POST /vote
  ▼
FastAPI
  │
  │ Validate request
  ▼
Authentication / Authorization
  │
  │ Generate / validate request_id
  ▼
Redis / ARQ Queue
  │
  ▼
ARQ Worker
  │
  ├── Validate voter
  ├── Validate candidate
  ├── Validate polling booth
  ├── Check idempotency
  ├── Persist voting record
  └── Record audit information
  │
  ▼
PostgreSQL

The request_id mechanism prevents duplicate processing of the same vote request.

📌 Core API Endpoints
Method    Endpoint    Description
POST    /auth/login    Authenticate a user
POST    /auth/refresh    Refresh authentication token
GET    /auth/me    Retrieve current user
POST    /constituencies    Create constituency
GET    /constituencies    List constituencies
POST    /booths    Create polling booth
GET    /booths    List polling booths
POST    /candidates    Register candidate
GET    /candidates    List candidates
POST    /voters    Register voter
GET    /voters    List voters
GET    /voters/{id}    Retrieve voter
POST    /vote    Submit a vote
GET    /health    Application health check

For the authoritative API contract, use the generated Swagger documentation:

http://localhost:8000/docs
🗃️ Database Schema

The platform contains the following primary tables:

users
constituencies
voters
candidates
polling_booths
voting_records
audit_logs
refresh_tokens

Key relationships include:

Constituency
 ├── Voters
 ├── Candidates
 └── Polling Booths

Voter
 └── Voting Records

Candidate
 └── Voting Records

Polling Booth
 └── Voting Records

User
 ├── Audit Logs
 ├── Refresh Tokens
 ├── Voters
 └── Candidates

The voting record maintains relationships to the voter, candidate, and polling booth while enforcing database-level foreign-key integrity.

🔄 Database Migration History

The final migration chain establishes the schema from an empty PostgreSQL database:

20577bf67e5c
    │
    ▼
002_performance_indexes
    │
    ▼
917949da489c
    │
    ▼
HEAD

Apply the complete chain with:

alembic upgrade head
🔄 CI/CD Pipeline

GitHub Actions performs automated validation on repository changes.

The pipeline validates:

Code
 │
 ├── Linting
 │
 ├── Test Suite
 │
 ├── Coverage
 │
 └── Docker Build / Compose Validation

A successful pipeline confirms that the application, tests, database integration, and Docker configuration remain valid in the CI environment.

📦 Requirements

Main dependencies include:

FastAPI
Uvicorn
SQLAlchemy
asyncpg
psycopg
aiosqlite
Alembic
ARQ
Redis
Pydantic
pydantic-settings
python-jose
Passlib
bcrypt
SlowAPI
Pytest
pytest-asyncio
pytest-cov
HTTPX
Factory Boy
Locust
Black
isort
mypy
Flake8
Bandit
pip-audit

See requirements.txt for the complete dependency specification.

📄 License

MIT License

👤 Author

sa-99nje-ev

GitHub: sa-99nje-ev

🏁 Project Status

COMPLETE ✅
The final implementation has been validated locally and through GitHub Actions.
Election Operations Platform — Final Version
