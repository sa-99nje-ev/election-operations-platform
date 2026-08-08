# Election Operations Platform

A production-oriented election operations platform built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, **ARQ**, and **Redis**.

The platform provides a secure asynchronous backend for election administration, voter management, candidate management, polling-booth operations, vote processing, audit logging, and election-result workflows.

---

## 📌 Project Overview

The Election Operations Platform is designed around a modular backend architecture with:

- FastAPI REST API
- PostgreSQL relational database
- SQLAlchemy 2.0 asynchronous ORM
- Alembic database migrations
- ARQ + Redis asynchronous background processing
- JWT-based authentication
- Role-based access control
- Secure password hashing
- Election-domain integrity constraints
- Audit logging
- Refresh-token management
- Performance and reliability testing
- Automated CI/CD validation
- Docker-based application validation
- Dashboard and analytics support

The system separates API handling, business logic, persistence, background processing, and testing concerns to provide a maintainable election-management backend.

---

## 🏗 Architecture

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
```

---

## ✨ Core Features

### 🔐 Authentication & Security
- JWT authentication
- Access-token handling
- Refresh-token storage and invalidation
- Password hashing using Passlib
- Role-based authorization
- Rate limiting support
- Security-oriented audit logging

### 🗳️ Election Operations
- Constituency management
- Candidate management
- Voter management
- Polling-booth management
- Vote submission pipeline
- Duplicate/idempotent vote-request protection
- Election-integrity validation
- Voting-record persistence
- Election-result retrieval

### ⚙️ Asynchronous Processing
Vote-processing operations are handled through an ARQ background worker backed by Redis.

The worker:
- Receives queued vote-processing tasks
- Validates voter/candidate/booth identifiers
- Prevents duplicate votes
- Persists voting records through SQLAlchemy
- Updates candidate tallies in Redis
- Handles database integrity errors
- Returns processing status and request IDs

This allows request handling and background processing to remain separated.

### 📋 Audit & Compliance
The platform maintains audit information for security-sensitive operations, including:
- Event type
- Actor
- Target
- Outcome
- IP address
- Timestamp

### 📊 Dashboard
The project includes a dashboard layer using:
- Dash
- Plotly

...for election-related analytics and visualization.

---

## 🗄️ Database

The platform uses PostgreSQL with SQLAlchemy 2.0's asynchronous ORM.

**Main Tables**
- users
- constituencies
- voters
- candidates
- polling_booths
- voting_records
- audit_logs
- refresh_tokens

**Entity Relationships**
- Constituency → Voters, Candidates, Polling Booths
- Voter → Voting Records
- Candidate → Voting Records
- Polling Booth → Voting Records
- User → Candidates, Voters, Audit Logs, Refresh Tokens

Voting records maintain relationships to voters, candidates, and polling booths while enforcing database-level foreign-key integrity.

### 🔄 Database Migration History

The final migration chain is:

```text
20577bf67e5c
     │
     ▼
002_performance_indexes
     │
     ▼
917949da489c
     │
    HEAD
```

- The initial migration establishes the application schema.
- The performance migration adds composite indexes for frequently accessed election-domain queries.
- The final migration represents the FastAPI/async migration state.

Apply the complete migration chain:
```bash
alembic upgrade head
```

Check the current migration:
```bash
alembic current
```

Display migration history:
```bash
alembic history
```

---

## 🔌 API

The platform exposes RESTful API endpoints for authentication, election-domain management, voting, health monitoring, and result retrieval.

### Core API Areas

- **Authentication** — User authentication and token management
- **Constituencies** — Constituency creation and retrieval
- **Candidates** — Candidate creation and retrieval
- **Voters** — Voter creation and retrieval
- **Polling Booths** — Booth creation and retrieval
- **Voting** — Vote submission and processing
- **Results** — Overall and constituency-level election results
- **Health** — API health monitoring

### Results Endpoints

- `GET /results/overall`
- `GET /results/constituency/{constituency_id}`

### Health Endpoint

- `GET /health`

---

## 🧪 Testing

The project contains automated unit, integration, domain, API, reliability, and performance-oriented tests.

Run the complete test suite:
```bash
pytest tests/ -v
```

Run the performance test suite:
```bash
pytest tests/performance/ -v
```

Run coverage analysis:
```bash
pytest --cov=app --cov-report=xml --cov-report=term-missing tests/
```

The test suite covers:
- API latency
- Database persistence
- Election integrity
- Vote submission pipeline
- Worker scaling
- System capacity under increasing workloads
- API health checks
- Domain access behavior
- Voting-service initialization
- Background vote-processing execution

The final local test suite successfully completed: **11 passed**

---

## 🔍 Code Quality

The project uses automated static-analysis and security-oriented tools including:
- Black
- isort
- mypy
- flake8
- Bandit
- pip-audit

Run the critical Flake8 checks:
```bash
flake8 app/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

Run the complete Flake8 check:
```bash
flake8 app/ tests/
```

Check Git whitespace errors:
```bash
git diff --check
```

---

## 🐳 Docker

The project includes Docker configuration for containerized application validation.

Build the application image:
```bash
docker compose build
```

Start the services:
```bash
docker compose up
```

Stop the services:
```bash
docker compose down
```

Docker build and Compose configuration are also validated through the CI pipeline.

---

## 🔁 CI/CD Pipeline

GitHub Actions automatically validates repository changes.

The CI pipeline performs:

```text
Repository Change
      │
      ▼
   Linting
      │
      ▼
 Test Suite
      │
      ▼
  Coverage
      │
      ▼
Docker Build / Compose Validation
```

The pipeline validates that:
- Application code passes linting
- Automated tests pass
- Coverage is generated
- Database-related functionality remains valid
- Docker configuration builds successfully
- Compose configuration remains valid

The final CI pipeline has been successfully validated through GitHub Actions.

---

## 📦 Requirements

Major dependencies include:
- FastAPI
- Uvicorn
- SQLAlchemy
- asyncpg / psycopg
- Alembic
- ARQ
- Redis
- Pydantic
- Pydantic Settings
- PyJWT
- Passlib
- bcrypt
- SlowAPI
- Dash
- Plotly
- pytest
- pytest-asyncio
- pytest-cov
- httpx
- Black
- isort
- mypy
- flake8
- Bandit
- pip-audit

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Local Setup

**1. Clone the repository**
```bash
git clone https://github.com/sa-99nje-ev/election-operations-platform.git
cd election-operations-platform
```

**2. Create a virtual environment**
```bash
python -m venv .venv
```

**3. Activate the virtual environment**

PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Configure environment variables**

Create a `.env` file containing the required application configuration:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/election_db
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET_KEY=your-secure-jwt-secret-key
SECRET_KEY=your-secure-secret-key
```

> **Note:** These are placeholders. Do not commit real credentials or secrets to the repository. For running tests, a `TEST_DATABASE_URL` may also be required.

**6. Apply database migrations**
```bash
alembic upgrade head
```

**7. Start the FastAPI application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
FastAPI's interactive documentation is available at `http://localhost:8000/docs`

---

## 📁 Project Structure

```text
election-operations-platform/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── domain.py
│   │   └── voting.py
│   │
│   ├── config/
│   │   └── ...
│   │
│   ├── core/
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
│   │   └── ...
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── booths.py
│   │   ├── candidates.py
│   │   ├── constituencies.py
│   │   ├── results.py
│   │   ├── vote.py
│   │   └── voters.py
│   │
│   ├── schemas/
│   │   └── ...
│   │
│   ├── services/
│   │   └── ...
│   │
│   ├── utils/
│   │   └── ...
│   │
│   ├── workers/
│   │   └── voting_worker.py
│   │
│   ├── database.py
│   └── main.py
│
├── migrations/
│   ├── env.py
│   └── versions/
│
├── tests/
│   ├── performance/
│   ├── unit/
│   ├── conftest.py
│   └── ...
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 🔒 Security Considerations

The application incorporates several security mechanisms:
- Password hashing
- JWT-based authentication
- Refresh-token invalidation
- Role-based authorization
- Database foreign-key constraints
- Request idempotency
- Audit logging
- Rate limiting
- Input validation through Pydantic
- Dependency vulnerability scanning
- Static security analysis

---

## 📈 Performance Considerations

The backend uses asynchronous components throughout the primary request and database-processing path.

Performance-oriented design decisions include:
- Async FastAPI endpoints
- Async SQLAlchemy sessions
- PostgreSQL connection pooling
- Indexed foreign-key and lookup columns
- Composite database indexes
- ARQ background workers
- Redis-backed asynchronous task processing
- Database-level integrity constraints
- Automated worker-scaling tests

---

## 🧩 Technology Stack

| Category | Technology |
|---|---|
| Backend | FastAPI |
| Server | Uvicorn |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| PostgreSQL Driver | asyncpg / psycopg |
| Migrations | Alembic |
| Background Jobs | ARQ |
| Message / Cache Layer | Redis |
| Validation | Pydantic |
| Authentication | JWT |
| Password Hashing | Passlib / bcrypt |
| Rate Limiting | SlowAPI |
| Dashboard | Dash |
| Visualization | Plotly |
| Testing | pytest |
| Async Testing | pytest-asyncio |
| HTTP Testing | HTTPX |
| Coverage | pytest-cov |
| Formatting | Black |
| Import Sorting | isort |
| Type Checking | mypy |
| Linting | flake8 |
| Security Analysis | Bandit |
| Dependency Auditing | pip-audit |
| Containerization | Docker |
| CI/CD | GitHub Actions |

---

## 📜 License

See the repository license file for licensing information.

## 👤 Author

**sa-99nje-ev**
GitHub: [sa-99nje-ev](https://github.com/sa-99nje-ev)

## 🚀 Project Status

**Final Version** — The final implementation has been validated locally and through GitHub Actions.
