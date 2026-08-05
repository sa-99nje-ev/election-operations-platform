# Election Operations Platform

A production-ready backend application for managing election workflows, built with FastAPI and async Python.

---

## 🚀 Features

- **Authentication & RBAC**: JWT-based authentication with role-based access control (Admin, Officer, Voter, Candidate)
- **Domain Management**: Full CRUD for constituencies, polling booths, voters, and candidates
- **Async Vote Processing**: Background task queue using ARQ + Redis for non-blocking vote recording
- **Audit Logging**: Comprehensive audit trail for all security-critical operations
- **Performance Testing**: Load testing with Locust and performance benchmarks with pytest
- **Database Migrations**: Alembic for version-controlled schema changes
- **Containerized Deployment**: Docker and Docker Compose support

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI 0.111+ |
| **Database** | PostgreSQL 15+ (Async SQLAlchemy 2.0) |
| **Task Queue** | ARQ + Redis |
| **Authentication** | JWT + bcrypt |
| **Testing** | Pytest, pytest-asyncio, HTTPX |
| **Load Testing** | Locust |
| **Deployment** | Docker, Docker Compose |
| **Migrations** | Alembic |

---

## 📦 Project Structure
election-operations-platform/
├── app/
│ ├── models/ # SQLAlchemy ORM models
│ ├── repositories/ # Data access layer
│ ├── services/ # Business logic
│ ├── routers/ # FastAPI endpoints
│ ├── schemas/ # Pydantic schemas
│ ├── core/ # Configuration & settings
│ └── workers/ # ARQ background workers
├── tests/
│ ├── performance/ # Performance benchmarks
│ ├── unit/ # Unit tests
│ └── integration/ # API integration tests
├── migrations/ # Alembic database migrations
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md

text

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 15+ (running)
- Redis 7+ (running)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/sa-99nje-ev/election-operations-platform.git
cd election-operations-platform
2. Create and activate virtual environment

bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
3. Install dependencies

bash
pip install -r requirements.txt
4. Configure environment variables

Create a .env file from .env.example:

bash
cp .env.example .env
Update the following values in .env:

ini
DATABASE_URL=postgresql://user:password@localhost:5432/election_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
5. Run database migrations

bash
alembic upgrade head
6. Start the FastAPI server

bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Access the interactive API docs at: http://localhost:8000/docs

7. Start the ARQ worker (for background tasks)

bash
arq worker --func app.workers.arq_worker.startup
🧪 Testing
Run all tests
bash
pytest -v --tb=short
Run only performance tests
bash
pytest tests/performance/ -v
Run with coverage
bash
pytest -v --cov=app --cov-report=term-missing
📊 Load Testing
Run Locust load testing:

bash
locust -f locustfile.py --host http://localhost:8000
Open http://localhost:8089 to configure and start the test.

🐳 Docker Deployment
Build and run with Docker Compose
bash
docker-compose up --build
Services started:

FastAPI app: http://localhost:8000

PostgreSQL: port 5432

Redis: port 6379

ARQ Worker: background processing

Stop services
bash
docker-compose down
📝 API Endpoints
Method    Endpoint    Description
POST    /auth/login    Login with username/password
POST    /auth/refresh    Refresh JWT token
GET    /auth/me    Get current user info
POST    /constituencies    Create constituency (Admin/Officer)
GET    /constituencies    List constituencies
POST    /booths    Create polling booth (Officer)
GET    /booths    List polling booths
POST    /candidates    Register candidate (Officer)
GET    /candidates    List candidates
POST    /voters    Register voter (Officer)
GET    /voters    List voters
GET    /voters/{id}    Get voter by ID
POST    /vote    Cast a vote (Voter)
GET    /health    Health check
Full API documentation available at /docs (Swagger UI).

📄 License
MIT License - see LICENSE file for details.

👤 Author
sa-99nje-ev

GitHub: @sa-99nje-ev

