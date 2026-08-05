# Election Operations Platform

A production-ready backend application for managing election workflows, built with **FastAPI** and **async Python**.

---

# 🚀 Features

- **Authentication & RBAC**
  - JWT-based authentication
  - Role-based access control (Admin, Officer, Voter, Candidate)

- **Domain Management**
  - Full CRUD for constituencies
  - Polling booths
  - Voters
  - Candidates

- **Async Vote Processing**
  - ARQ + Redis background queue
  - Non-blocking vote recording

- **Audit Logging**
  - Complete audit trail for security-critical operations

- **Performance Testing**
  - Pytest benchmark suite
  - Locust load testing

- **Database Migrations**
  - Alembic version-controlled schema migrations

- **Containerized Deployment**
  - Docker
  - Docker Compose

---

# 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.111+ |
| Database | PostgreSQL 15+ (Async SQLAlchemy 2.0) |
| Task Queue | ARQ + Redis |
| Authentication | JWT + bcrypt |
| Testing | Pytest, pytest-asyncio, HTTPX |
| Load Testing | Locust |
| Deployment | Docker, Docker Compose |
| Migrations | Alembic |

---

# 📁 Project Structure

```text
election-operations-platform/
│
├── app/
│   ├── models/             # SQLAlchemy ORM models
│   ├── repositories/       # Data access layer
│   ├── services/           # Business logic
│   ├── routers/            # FastAPI endpoints
│   ├── schemas/            # Pydantic schemas
│   ├── core/               # Configuration & settings
│   └── workers/            # ARQ background workers
│
├── tests/
│   ├── performance/        # Performance benchmarks
│   ├── unit/               # Unit tests
│   └── integration/        # API integration tests
│
├── migrations/             # Alembic database migrations
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

- Python 3.10+
- PostgreSQL 15+ (running)
- Redis 7+ (running)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sa-99nje-ev/election-operations-platform.git

cd election-operations-platform
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create the `.env` file.

```bash
cp .env.example .env
```

Update the values.

```env
DATABASE_URL=postgresql://user:password@localhost:5432/election_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

---

### 5. Apply database migrations

```bash
alembic upgrade head
```

---

### 6. Start the FastAPI server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI

```
http://localhost:8000/docs
```

---

### 7. Start the ARQ Worker

```bash
arq worker app.workers.arq_worker.WorkerSettings
```

*(Replace with the actual worker module used in your project if different.)*

---

# 🧪 Testing

Run all tests

```bash
pytest -v --tb=short
```

Run performance tests

```bash
pytest tests/performance -v
```

Run coverage

```bash
pytest -v --cov=app --cov-report=term-missing
```

---

# 📊 Load Testing

```bash
locust -f locustfile.py --host http://localhost:8000
```

Open

```
http://localhost:8089
```

to configure the load test.

---

# 🐳 Docker Deployment

Build and start

```bash
docker-compose up --build
```

Services

- FastAPI → http://localhost:8000
- PostgreSQL → localhost:5432
- Redis → localhost:6379
- ARQ Worker

Stop services

```bash
docker-compose down
```

---

# 📌 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/login` | Login |
| POST | `/auth/refresh` | Refresh JWT |
| GET | `/auth/me` | Current user |
| POST | `/constituencies` | Create constituency |
| GET | `/constituencies` | List constituencies |
| POST | `/booths` | Create polling booth |
| GET | `/booths` | List polling booths |
| POST | `/candidates` | Register candidate |
| GET | `/candidates` | List candidates |
| POST | `/voters` | Register voter |
| GET | `/voters` | List voters |
| GET | `/voters/{id}` | Get voter |
| POST | `/vote` | Cast vote |
| GET | `/health` | Health check |

Swagger Documentation

```
http://localhost:8000/docs
```

---

# 📄 License

MIT License

---

# 👤 Author

**sa-99nje-ev**

GitHub: **https://github.com/sa-99nje-ev**
