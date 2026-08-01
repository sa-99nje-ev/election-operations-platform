# Election Operations Platform

A production-quality backend system designed to manage complete election workflows while remaining responsive during peak polling traffic. The platform handles voter and candidate registration, secure JWT-based role access, asynchronous vote processing via a Redis/Celery pipeline, a live operations dashboard, and load simulation tooling.

## Overview

The Election Operations Platform is built as a modular monolith using Python/Flask with:
- **Voter & Candidate Registration**: Manage eligible voters and candidates per constituency
- **Secure Authentication**: JWT-based authentication with role-based access control (RBAC)
- **Asynchronous Vote Processing**: Redis/Celery pipeline for responsive vote submission
- **Real-time Dashboard**: Plotly Dash operations dashboard for live election metrics
- **Load Simulation**: Built-in Locust testing for performance validation
- **Containerized Deployment**: Docker Compose for reproducible environments

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd election-operations-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   flask db upgrade
   ```

6. **Start the application**
   ```bash
   flask run
   ```

### Docker Deployment

```bash
docker compose up
```

The platform will be available at:
- API Server: http://localhost:5000
- Dashboard: http://localhost:8050
- Load Testing UI: http://localhost:8089

## Project Structure

```
election-operations-platform/
├── app/                    # Main application package
│   ├── api/               # REST API endpoints
│   ├── auth/              # Authentication & authorization
│   ├── config/            # Configuration management
│   ├── models/            # SQLAlchemy ORM models
│   ├── repositories/      # Data access layer
│   ├── services/          # Business logic layer
│   ├── schemas/           # Request/response validation
│   ├── utils/             # Shared utilities
│   └── extensions.py      # Flask extensions
├── tasks/                 # Celery task definitions
├── dashboard/             # Plotly Dash application
├── tests/                 # Test suites
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── load/             # Load tests
├── scripts/               # Utility scripts
├── migrations/            # Alembic migration files
└── docker/                # Docker configuration
```

## Technology Stack

- **Backend**: Flask 3.0
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0
- **Authentication**: Flask-JWT-Extended
- **Async Processing**: Celery 5.x + Redis 7.x
- **Dashboard**: Plotly Dash
- **Load Testing**: Locust
- **Containerization**: Docker + Docker Compose

## Development

For detailed implementation documentation, see:
- [Requirements Document](.kiro/specs/election-operations-platform/requirements.md)
- [Technical Design](.kiro/specs/election-operations-platform/design.md)
- [Implementation Tasks](.kiro/specs/election-operations-platform/tasks.md)

## License

Proprietary - All Rights Reserved
