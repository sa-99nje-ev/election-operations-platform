# Technical Design Document

## 1. Introduction

### System Overview

The Election Operations Platform is a production-quality backend system built as a **modular monolith** to manage complete election workflows. The platform handles voter and candidate registration, secure JWT-based authentication with role-based access control, asynchronous vote processing via a Redis/Celery pipeline, real-time operational dashboards, and load simulation tooling.

### Core Engineering Problems Addressed

1. **Preventing duplicate votes under concurrency** — PostgreSQL transactions with unique constraints ensure exactly-once vote recording
2. **Maintaining API responsiveness during peak traffic** — Asynchronous vote processing decouples vote acceptance from persistence
3. **Real-time operational visibility** — Live dashboard provides election officers with system health and metrics
4. **Performance validation** — Built-in load simulation identifies bottlenecks before election day

### Key Design Principles

- **Modular Monolith**: All components run within a single Flask application with clear module boundaries
- **Single Responsibility**: Each module has one well-defined purpose
- **Separation of Concerns**: API, business logic, and data access are cleanly separated
- **KISS (Keep It Simple)**: No microservices, no distributed systems patterns, no unnecessary complexity
- **YAGNI (You Aren't Gonna Need It)**: No speculative features or premature optimization
- **Transaction-Driven Integrity**: Leverage PostgreSQL ACID guarantees rather than distributed locks

---

## 2. Architecture Overview

### 2.1 Architectural Style

**Modular Monolith Architecture**

All components run within a single Flask application process with clear module boundaries. This architecture provides:
- Simple deployment (single process + workers)
- Straightforward debugging and testing
- Easy local development
- No network latency between modules
- ACID transaction guarantees across operations

### 2.2 High-Level System Diagram

```mermaid
graph TB
    subgraph "External Actors"
        Admin[Administrator]
        Officer[Election Officer]
        Polling[Polling Officer]
        Voter[Voter]
        Candidate[Candidate]
    end

    subgraph "Election Operations Platform"
        API[API Server<br/>Flask Application]
        Workers[Celery Workers<br/>Background Processing]
        Dashboard[Dashboard<br/>Plotly Dash]
        
        subgraph "Data Layer"
            PostgreSQL[(PostgreSQL<br/>Primary Data Store)]
            Redis[(Redis<br/>Task Queue)]
        end
    end
    
    LoadSim[Load Simulator<br/>Locust]
    
    Admin --> API
    Officer --> API
    Polling --> API
    Voter --> API
    Candidate --> API
    
    API --> PostgreSQL
    API --> Redis
    Workers --> Redis
    Workers --> PostgreSQL
    Dashboard --> PostgreSQL
    Dashboard --> Redis
    LoadSim --> API
```

### 2.3 Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Backend Framework** | Flask (Application Factory Pattern) | Lightweight, well-documented, ideal for RESTful APIs and moderate-scale projects |
| **Database** | PostgreSQL 15+ | ACID compliance, robust constraints, mature ecosystem |
| **ORM** | SQLAlchemy 2.0+ | Type safety, abstracts SQL, integrates with Alembic |
| **Migrations** | Alembic | Industry standard for SQLAlchemy schema versioning |
| **Authentication** | Flask-JWT-Extended | Mature JWT implementation with refresh token support |
| **Async Processing** | Celery 5.x | Mature, well-supported async task queue for Python |
| **Message Broker** | Redis 7.x | High performance, simple setup, adequate for this scale |
| **Dashboard** | Plotly Dash | Python-native, integrates with Flask, real-time updates |
| **Load Testing** | Locust | Python-based, programmable, generates detailed metrics |
| **Containerization** | Docker + Docker Compose | Reproducible environments, simple deployment |
| **Configuration** | python-dotenv | Environment-based config, 12-factor app compliance |

---

## 3. Module Design

### 3.1 Module Structure

```
election-operations-platform/
├── app/
│   ├── __init__.py                # Application factory
│   ├── api/                       # REST API endpoints (routes/controllers)
│   │   ├── __init__.py
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── users.py               # User management endpoints
│   │   ├── voters.py              # Voter management endpoints
│   │   ├── candidates.py          # Candidate management endpoints
│   │   ├── booths.py              # Polling booth endpoints
│   │   ├── votes.py               # Vote submission and status
│   │   ├── results.py             # Election results endpoints
│   │   └── audit.py               # Audit log query endpoints
│   ├── auth/                      # Authentication and authorization logic
│   │   ├── __init__.py
│   │   ├── jwt_manager.py         # JWT token generation and validation
│   │   ├── decorators.py          # RBAC decorators (@require_role)
│   │   └── password.py            # Password hashing utilities
│   ├── config/                    # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py            # Environment-based configuration classes
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                # User model
│   │   ├── voter.py               # Voter model
│   │   ├── candidate.py           # Candidate model
│   │   ├── constituency.py        # Constituency model
│   │   ├── polling_booth.py       # Polling booth model
│   │   ├── voting_record.py       # Voting record model
│   │   ├── audit_log.py           # Audit log model
│   │   └── refresh_token.py       # Refresh token model
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                # Base repository with common operations
│   │   ├── user_repository.py
│   │   ├── voter_repository.py
│   │   ├── candidate_repository.py
│   │   ├── constituency_repository.py
│   │   ├── polling_booth_repository.py
│   │   ├── voting_record_repository.py
│   │   ├── audit_log_repository.py
│   │   └── refresh_token_repository.py
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Authentication business logic
│   │   ├── user_service.py        # User management logic
│   │   ├── voter_service.py       # Voter registration logic
│   │   ├── candidate_service.py   # Candidate registration logic
│   │   ├── polling_booth_service.py
│   │   ├── vote_service.py        # Vote submission orchestration
│   │   ├── results_service.py     # Results aggregation logic
│   │   └── audit_service.py       # Audit logging logic
│   ├── schemas/                   # Request/response validation
│   │   ├── __init__.py
│   │   ├── auth_schemas.py        # Login, refresh, logout schemas
│   │   ├── user_schemas.py
│   │   ├── voter_schemas.py
│   │   ├── candidate_schemas.py
│   │   ├── polling_booth_schemas.py
│   │   ├── vote_schemas.py
│   │   └── results_schemas.py
│   ├── utils/                     # Shared utilities
│   │   ├── __init__.py
│   │   ├── validators.py          # Custom validation functions
│   │   ├── exceptions.py          # Custom exception classes
│   │   └── helpers.py             # General helper functions
│   └── extensions.py              # Flask extension initialization (db, jwt, etc.)
├── tasks/                         # Celery task definitions
│   ├── __init__.py
│   ├── celery_app.py              # Celery application factory
│   └── voting.py                  # Vote processing tasks
├── dashboard/                     # Plotly Dash application
│   ├── __init__.py
│   ├── app.py                     # Dash application factory
│   ├── layouts.py                 # Dashboard UI layouts
│   └── callbacks.py               # Real-time update callbacks
├── tests/                         # Test suites
│   ├── unit/
│   ├── integration/
│   └── load/
├── scripts/                       # Utility scripts
│   ├── seed_data.py               # Database seeding
│   └── create_admin.py            # Admin user creation
├── migrations/                    # Alembic migration files
│   └── versions/
├── docker/                        # Docker configuration
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   ├── Dockerfile.dashboard
│   └── docker-compose.yml
├── .env.example                   # Example environment configuration
├── requirements.txt               # Python dependencies
└── README.md
```

### 3.2 Module Responsibilities

#### app/api/ — REST API Endpoints

**Responsibility**: Handle HTTP request routing, request validation, response formatting

**Public Interface**:
- Flask blueprints registered with the application factory
- REST endpoints for all platform operations

**Dependencies**: Services, Schemas, Auth decorators

**Key Components**:
- `auth.py`: POST /api/auth/login, /api/auth/refresh, /api/auth/logout
- `voters.py`: POST /api/voters, GET /api/voters, GET /api/voters/{id}
- `votes.py`: POST /api/votes, GET /api/votes/status/{task_id}
- `results.py`: GET /api/results/{constituency_id}

**Design Pattern**: Thin controllers — validation and serialization only, business logic delegated to services

---

#### app/auth/ — Authentication and Authorization

**Responsibility**: JWT token management, RBAC enforcement, password security

**Public Interface**:
- `jwt_manager.create_access_token(identity, role)`
- `jwt_manager.create_refresh_token(identity)`
- `@require_role('Admin', 'Election_Officer')` decorator

**Dependencies**: Flask-JWT-Extended, bcrypt

**Key Components**:
- `jwt_manager.py`: Token generation, validation, blacklisting
- `decorators.py`: Role-based access control decorators
- `password.py`: Bcrypt hashing (cost factor 12)

---

#### app/config/ — Configuration Management

**Responsibility**: Environment-based configuration loading, validation

**Public Interface**:
- `Config` base class
- `DevelopmentConfig`, `TestingConfig`, `ProductionConfig` subclasses

**Dependencies**: python-dotenv, os.environ

**Key Components**:
- `settings.py`: Configuration classes with validation

**Design Pattern**: 12-factor app — all config from environment variables

---

#### app/models/ — SQLAlchemy ORM Models

**Responsibility**: Database schema representation, relationships, constraints

**Public Interface**: ORM model classes with relationships

**Dependencies**: SQLAlchemy, UUID

**Key Components**:
- `user.py`: User(id UUID, username, password_hash, role, created_at)
- `voter.py`: Voter(id UUID, national_id, full_name, dob, constituency_id, status)
- `voting_record.py`: VotingRecord(id UUID, voter_id UNIQUE, candidate_id, booth_id, voted_at)
- `audit_log.py`: AuditLog(id UUID, event_type, actor_id, target_id, outcome, ip_address, created_at)

**Design Pattern**: Anemic domain model — models are data containers, business logic in services

---

#### app/repositories/ — Data Access Layer

**Responsibility**: Abstract database operations, provide clean query interface

**Public Interface**:
- `create(entity)`, `get_by_id(id)`, `update(entity)`, `delete(id)`
- Domain-specific queries (e.g., `get_voter_by_national_id()`)

**Dependencies**: SQLAlchemy session, models

**Key Components**:
- `base.py`: BaseRepository with CRUD operations
- Specialized repositories inherit from BaseRepository

**Design Pattern**: Repository pattern — decouples business logic from data access, makes testing easier

---

#### app/services/ — Business Logic Layer

**Responsibility**: Orchestrate business operations, enforce business rules, coordinate repositories

**Public Interface**:
- `auth_service.authenticate(username, password)`
- `vote_service.submit_vote(voter_id, candidate_id, booth_id)`
- `results_service.get_constituency_results(constituency_id)`

**Dependencies**: Repositories, Celery tasks, Audit service

**Key Components**:
- `auth_service.py`: Login, token refresh, logout logic
- `vote_service.py`: Pre-submission validation, task enqueueing, duplicate detection
- `results_service.py`: Results aggregation with optimized queries

**Design Pattern**: Service layer — centralizes business logic, prevents fat models and fat controllers

---

#### app/schemas/ — Request/Response Validation

**Responsibility**: Input validation, serialization, deserialization

**Public Interface**: Marshmallow or Pydantic schema classes

**Dependencies**: Marshmallow or Pydantic

**Key Components**:
- `voter_schemas.py`: VoterRegistrationSchema(national_id, full_name, dob, constituency_id)
- `vote_schemas.py`: VoteSubmissionSchema(candidate_id, booth_id)

**Design Pattern**: Data Transfer Objects (DTOs) — clean boundary between API and business logic

---

#### tasks/ — Celery Task Definitions

**Responsibility**: Asynchronous background processing, vote persistence

**Public Interface**: Celery task decorators

**Dependencies**: Celery, Repositories, PostgreSQL session

**Key Components**:
- `voting.py`: `process_vote(voter_id, candidate_id, booth_id, timestamp)` task

**Design Pattern**: Task queue — decouples API responsiveness from heavy operations

---

#### dashboard/ — Plotly Dash Application

**Responsibility**: Real-time metrics visualization, system health monitoring

**Public Interface**: Web UI accessible at http://localhost:8050

**Dependencies**: Plotly Dash, PostgreSQL, Redis, Celery inspect API

**Key Components**:
- `app.py`: Dash application factory with JWT authentication
- `layouts.py`: Dashboard UI components (graphs, tables, alerts)
- `callbacks.py`: Real-time data refresh (every 10 seconds)

---

## 4. Database Design

### 4.1 Entity-Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Voter : "may have"
    User ||--o{ Candidate : "may have"
    User ||--o{ RefreshToken : "has"
    User ||--o{ AuditLog : "performs"
    
    Constituency ||--o{ Voter : "contains"
    Constituency ||--o{ Candidate : "contains"
    Constituency ||--o{ PollingBooth : "contains"
    
    PollingBooth ||--o{ VotingRecord : "records"
    
    Voter ||--o| VotingRecord : "casts"
    Candidate ||--o{ VotingRecord : "receives"
    
    User {
        uuid id PK
        varchar username UK
        varchar password_hash
        varchar role
        timestamptz created_at
    }
    
    Voter {
        uuid id PK
        varchar national_id UK
        varchar full_name
        date dob
        uuid constituency_id FK
        uuid user_id FK
        varchar status
    }
    
    Candidate {
        uuid id PK
        varchar national_id UK
        varchar full_name
        varchar party
        uuid constituency_id FK
        uuid user_id FK
    }
    
    Constituency {
        uuid id PK
        varchar name UK
        varchar region
    }
    
    PollingBooth {
        uuid id PK
        varchar booth_code UK
        varchar location
        integer capacity
        uuid constituency_id FK
        varchar status
    }
    
    VotingRecord {
        uuid id PK
        uuid voter_id FK,UK
        uuid candidate_id FK
        uuid booth_id FK
        timestamptz voted_at
    }
    
    AuditLog {
        uuid id PK
        varchar event_type
        uuid actor_id FK
        uuid target_id
        varchar outcome
        varchar ip_address
        timestamptz created_at
    }
    
    RefreshToken {
        uuid id PK
        uuid user_id FK
        varchar token_hash UK
        timestamptz expires_at
        boolean invalidated
    }
```

### 4.2 Table Definitions

#### users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier (UUID v4) |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Login username |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hash (cost factor 12) |
| role | VARCHAR(20) | NOT NULL | One of: Admin, Election_Officer, Polling_Officer, Candidate, Voter |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Account creation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `username`

---

#### voters

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique voter identifier (UUID v4) |
| national_id | VARCHAR(50) | UNIQUE, NOT NULL | Government-issued ID |
| full_name | VARCHAR(100) | NOT NULL | Voter's full name |
| dob | DATE | NOT NULL | Date of birth |
| constituency_id | UUID | FOREIGN KEY → constituencies(id), NOT NULL | Assigned constituency |
| user_id | UUID | FOREIGN KEY → users(id) | Associated user account |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | One of: active, inactive |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `national_id`
- Index on `constituency_id` (for results queries)

**Constraints**:
- FOREIGN KEY `constituency_id` REFERENCES `constituencies(id)` ON DELETE RESTRICT
- FOREIGN KEY `user_id` REFERENCES `users(id)` ON DELETE RESTRICT

---

#### candidates

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique candidate identifier (UUID v4) |
| national_id | VARCHAR(50) | UNIQUE, NOT NULL | Government-issued ID |
| full_name | VARCHAR(100) | NOT NULL | Candidate's full name |
| party | VARCHAR(100) | NOT NULL | Political party affiliation |
| constituency_id | UUID | FOREIGN KEY → constituencies(id), NOT NULL | Constituency contesting |
| user_id | UUID | FOREIGN KEY → users(id) | Associated user account |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `national_id`
- Index on `constituency_id` (for results queries)

**Constraints**:
- FOREIGN KEY `constituency_id` REFERENCES `constituencies(id)` ON DELETE RESTRICT
- FOREIGN KEY `user_id` REFERENCES `users(id)` ON DELETE RESTRICT
- CHECK constraint: Maximum 20 candidates per constituency (enforced at application layer due to complexity)

---

#### constituencies

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique constituency identifier (UUID v4) |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Constituency name |
| region | VARCHAR(100) | NOT NULL | Geographic region |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `name`

---

#### polling_booths

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique booth identifier (UUID v4) |
| booth_code | VARCHAR(20) | UNIQUE, NOT NULL | Alphanumeric booth code |
| location | VARCHAR(255) | NOT NULL | Physical address |
| capacity | INTEGER | NOT NULL, CHECK (capacity BETWEEN 1 AND 10000) | Maximum voter capacity |
| constituency_id | UUID | FOREIGN KEY → constituencies(id), NOT NULL | Assigned constituency |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'CLOSED' | One of: OPEN, CLOSED |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `booth_code`
- Index on `constituency_id`

**Constraints**:
- FOREIGN KEY `constituency_id` REFERENCES `constituencies(id)` ON DELETE RESTRICT

---

#### voting_records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique vote identifier (UUID v4) |
| voter_id | UUID | FOREIGN KEY → voters(id), UNIQUE, NOT NULL | Voter who cast the vote |
| candidate_id | UUID | FOREIGN KEY → candidates(id), NOT NULL | Candidate who received the vote |
| booth_id | UUID | FOREIGN KEY → polling_booths(id), NOT NULL | Booth where vote was cast |
| voted_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Vote timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- **UNIQUE index on `voter_id`** (CRITICAL: prevents duplicate votes)
- Index on `candidate_id` (for results aggregation)
- Index on `constituency_id` (derived via JOIN for results queries)
- Composite index on `(candidate_id, booth_id)` (for per-booth results)

**Constraints**:
- FOREIGN KEY `voter_id` REFERENCES `voters(id)` ON DELETE RESTRICT
- FOREIGN KEY `candidate_id` REFERENCES `candidates(id)` ON DELETE RESTRICT
- FOREIGN KEY `booth_id` REFERENCES `polling_booths(id)` ON DELETE RESTRICT

**Critical Design Note**: The UNIQUE constraint on `voter_id` is the primary mechanism preventing duplicate votes. When a Celery worker attempts to insert a second vote for the same voter, PostgreSQL will raise an `IntegrityError`, causing the transaction to roll back.

---

#### audit_logs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique log entry identifier (UUID v4) |
| event_type | VARCHAR(50) | NOT NULL | Event category (login, vote_submitted, etc.) |
| actor_id | UUID | FOREIGN KEY → users(id) | User who performed the action |
| target_id | UUID | | Resource affected (voter_id, candidate_id, etc.) |
| outcome | VARCHAR(20) | NOT NULL | One of: success, failure |
| ip_address | VARCHAR(45) | | Source IP (supports IPv6) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Event timestamp (millisecond precision) |

**Indexes**:
- PRIMARY KEY on `id`
- Index on `event_type` (for filtered queries)
- Index on `actor_id` (for user activity queries)
- Index on `created_at` (for time-range queries)

**Constraints**:
- FOREIGN KEY `actor_id` REFERENCES `users(id)` ON DELETE RESTRICT
- Append-only table: No UPDATE or DELETE operations permitted via API

---

#### refresh_tokens

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique token identifier (UUID v4) |
| user_id | UUID | FOREIGN KEY → users(id), NOT NULL | Token owner |
| token_hash | VARCHAR(255) | UNIQUE, NOT NULL | SHA-256 hash of refresh token |
| expires_at | TIMESTAMPTZ | NOT NULL | Token expiration timestamp (7 days from issue) |
| invalidated | BOOLEAN | NOT NULL, DEFAULT FALSE | Logout flag |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `token_hash` (for token lookup)
- Index on `user_id` (for user logout — invalidate all tokens)

**Constraints**:
- FOREIGN KEY `user_id` REFERENCES `users(id)` ON DELETE CASCADE

---

### 4.3 Key Design Decisions

#### Why UUID v4 Primary Keys?

- **Security**: Prevents enumeration attacks (e.g., iterating `/api/voters/1`, `/api/voters/2`, ...)
- **Distributed-Ready**: Allows ID generation without central coordination (future-proof)
- **Privacy**: Non-sequential IDs don't leak registration order or volume

#### Why UNIQUE Constraint on voting_records.voter_id?

- **Idempotency**: PostgreSQL enforces exactly-once semantics at the database level
- **Concurrency-Safe**: Multiple Celery workers cannot insert duplicate votes even under race conditions
- **Simplicity**: No need for distributed locks or two-phase commits

#### Why ON DELETE RESTRICT?

- **Data Integrity**: Prevents accidental orphaning of related records
- **Audit Trail**: Ensures election data cannot be silently deleted
- **Explicit Deletion**: Forces application logic to handle cascading deletes explicitly

#### Why TIMESTAMPTZ for all timestamps?

- **UTC Storage**: Eliminates timezone ambiguity
- **ISO 8601 Compliance**: Standard format for audit logs and API responses
- **Future-Proof**: Supports distributed deployments across timezones

---

## 5. API Design

### 5.1 Authentication Endpoints

#### POST /api/auth/login

**Description**: Authenticate user and issue JWT tokens

**Authorization**: None (public endpoint)

**Request Body**:
```json
{
  "username": "string (1-50 chars, required)",
  "password": "string (8-128 chars, required)"
}
```

**Success Response** (200 OK):
```json
{
  "access_token": "string (JWT, 15-minute expiry)",
  "refresh_token": "string (JWT, 7-day expiry)",
  "user": {
    "id": "uuid",
    "username": "string",
    "role": "string"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials (generic message: "Invalid credentials")
- `422 Unprocessable Entity`: Missing or malformed fields

---

#### POST /api/auth/refresh

**Description**: Exchange refresh token for new access + refresh tokens

**Authorization**: Bearer token (refresh token)

**Request Body**:
```json
{
  "refresh_token": "string (JWT, required)"
}
```

**Success Response** (200 OK):
```json
{
  "access_token": "string (JWT, 15-minute expiry)",
  "refresh_token": "string (JWT, 7-day expiry)"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid, expired, or invalidated refresh token

---

#### POST /api/auth/logout

**Description**: Invalidate refresh token

**Authorization**: Bearer token (access token)

**Request Body**: None

**Success Response** (204 No Content)

**Error Responses**:
- `401 Unauthorized`: Missing or invalid access token

---

### 5.2 User Management Endpoints

#### POST /api/users

**Description**: Create a new user account

**Authorization**: Admin only

**Request Body**:
```json
{
  "username": "string (1-50 chars, unique, required)",
  "password": "string (8-128 chars, required)",
  "role": "string (one of: Admin, Election_Officer, Polling_Officer, Candidate, Voter, required)"
}
```

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "username": "string",
  "role": "string",
  "created_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Non-admin user
- `409 Conflict`: Username already exists
- `422 Unprocessable Entity`: Invalid field values

---

#### GET /api/users

**Description**: List all users (paginated)

**Authorization**: Admin only

**Query Parameters**:
- `page` (integer, default 1)
- `per_page` (integer, default 20, max 100)

**Success Response** (200 OK):
```json
{
  "users": [
    {
      "id": "uuid",
      "username": "string",
      "role": "string",
      "created_at": "ISO 8601 timestamp"
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 20
}
```

---

### 5.3 Voter Management Endpoints

#### POST /api/voters

**Description**: Register a new voter

**Authorization**: Admin or Election_Officer

**Request Body**:
```json
{
  "national_id": "string (1-50 chars, unique, required)",
  "full_name": "string (1-100 chars, required)",
  "dob": "string (ISO 8601 date, required)",
  "constituency_id": "uuid (required)"
}
```

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "national_id": "string (masked: *****1234)",
  "full_name": "string",
  "dob": "ISO 8601 date",
  "constituency_id": "uuid",
  "status": "active",
  "audit_logged": true
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient role permissions
- `409 Conflict`: National ID already registered
- `422 Unprocessable Entity`: Invalid field values or missing fields
- `503 Service Unavailable`: Audit log unavailable (registration rejected)

---

#### GET /api/voters

**Description**: List all voters (paginated, filterable by constituency)

**Authorization**: Admin or Election_Officer

**Query Parameters**:
- `page` (integer, default 1)
- `per_page` (integer, default 20, max 100)
- `constituency_id` (uuid, optional filter)

**Success Response** (200 OK):
```json
{
  "voters": [
    {
      "id": "uuid",
      "national_id": "string (masked)",
      "full_name": "string",
      "dob": "ISO 8601 date",
      "constituency_id": "uuid",
      "status": "active"
    }
  ],
  "total": 1500,
  "page": 1,
  "per_page": 20
}
```

---

### 5.4 Candidate Management Endpoints

#### POST /api/candidates

**Description**: Register a new candidate

**Authorization**: Election_Officer

**Request Body**:
```json
{
  "national_id": "string (1-50 chars, unique, required)",
  "full_name": "string (1-100 chars, required)",
  "party": "string (1-100 chars, required)",
  "constituency_id": "uuid (required)"
}
```

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "national_id": "string",
  "full_name": "string",
  "party": "string",
  "constituency_id": "uuid"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient role permissions
- `409 Conflict`: National ID already registered
- `422 Unprocessable Entity`: Invalid fields, constituency doesn't exist, or constituency has 20 candidates

---

#### GET /api/candidates

**Description**: List all candidates (filterable by constituency)

**Authorization**: Any authenticated user

**Query Parameters**:
- `constituency_id` (uuid, optional filter)

**Success Response** (200 OK):
```json
{
  "candidates": [
    {
      "id": "uuid",
      "full_name": "string",
      "party": "string",
      "constituency_id": "uuid"
    }
  ]
}
```

---

### 5.5 Polling Booth Endpoints

#### POST /api/booths

**Description**: Create a new polling booth

**Authorization**: Election_Officer

**Request Body**:
```json
{
  "booth_code": "string (1-20 alphanumeric, unique, required)",
  "location": "string (1-255 chars, required)",
  "capacity": "integer (1-10000, required)",
  "constituency_id": "uuid (required)"
}
```

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "booth_code": "string",
  "location": "string",
  "capacity": 500,
  "constituency_id": "uuid",
  "status": "CLOSED"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient role permissions
- `409 Conflict`: Booth code already exists
- `422 Unprocessable Entity`: Invalid fields or constituency doesn't exist

---

#### PATCH /api/booths/{id}/open

**Description**: Open a polling booth (transition from CLOSED to OPEN)

**Authorization**: Polling_Officer (assigned to this booth only)

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "booth_code": "string",
  "status": "OPEN",
  "opened_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Officer not assigned to this booth
- `409 Conflict`: Booth already OPEN
- `422 Unprocessable Entity`: Outside election day window

---

#### PATCH /api/booths/{id}/close

**Description**: Close a polling booth (transition from OPEN to CLOSED)

**Authorization**: Polling_Officer (assigned to this booth only)

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "booth_code": "string",
  "status": "CLOSED",
  "closed_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Officer not assigned to this booth
- `409 Conflict`: Booth already CLOSED

---

### 5.6 Vote Submission Endpoints

#### POST /api/votes

**Description**: Submit a vote (asynchronous processing)

**Authorization**: Voter

**Request Body**:
```json
{
  "candidate_id": "uuid (required)",
  "booth_id": "uuid (required)"
}
```

**Success Response** (202 Accepted):
```json
{
  "task_id": "uuid",
  "status": "QUEUED",
  "message": "Vote submitted successfully. Use task_id to check processing status."
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: User is not a Voter
- `409 Conflict`: Voter has already voted (existing voting_record or pending task)
- `422 Unprocessable Entity`: Candidate not in voter's constituency, booth is CLOSED, or invalid IDs
- `503 Service Unavailable`: Redis queue unavailable

**Processing Flow**:
1. API validates voter eligibility (checks PostgreSQL for existing voting_record)
2. If eligible, enqueue task to Redis via Celery
3. Return HTTP 202 immediately
4. Celery worker processes task asynchronously

---

#### GET /api/votes/status/{task_id}

**Description**: Check vote processing status

**Authorization**: Voter (can only check own tasks)

**Path Parameters**:
- `task_id` (uuid)

**Success Response** (200 OK):
```json
{
  "task_id": "uuid",
  "status": "COMPLETED | QUEUED | PROCESSING | FAILED",
  "updated_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Task does not belong to requesting user
- `404 Not Found`: Task ID does not exist

---

### 5.7 Election Results Endpoints

#### GET /api/results/{constituency_id}

**Description**: Retrieve vote tallies for a constituency

**Authorization**: Candidate (own constituency only), Election_Officer (any constituency)

**Path Parameters**:
- `constituency_id` (uuid)

**Success Response** (200 OK):
```json
{
  "constituency_id": "uuid",
  "constituency_name": "string",
  "total_votes": 1250,
  "total_registered_voters": 2000,
  "turnout_percentage": 62.50,
  "results": [
    {
      "candidate_id": "uuid",
      "candidate_name": "string",
      "party": "string",
      "vote_count": 450,
      "vote_percentage": 36.00
    },
    {
      "candidate_id": "uuid",
      "candidate_name": "string",
      "party": "string",
      "vote_count": 0,
      "vote_percentage": 0.00
    }
  ],
  "generated_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Candidate requesting results for different constituency
- `404 Not Found`: Constituency does not exist

**Performance Optimization**:
- Index on `voting_records(candidate_id, constituency_id)` for efficient aggregation
- Query uses `COUNT(*)` with `GROUP BY candidate_id`
- Includes candidates with zero votes (LEFT JOIN)

---

### 5.8 Audit Log Endpoints

#### GET /api/audit-logs

**Description**: Retrieve paginated audit logs with filtering

**Authorization**: Admin only

**Query Parameters**:
- `page` (integer, default 1)
- `per_page` (integer, default 100, max 100)
- `event_type` (string, optional filter)
- `actor_id` (uuid, optional filter)
- `start_time` (ISO 8601 timestamp, optional)
- `end_time` (ISO 8601 timestamp, optional)

**Success Response** (200 OK):
```json
{
  "logs": [
    {
      "id": "uuid",
      "event_type": "vote_submitted",
      "actor_id": "uuid",
      "target_id": "uuid",
      "outcome": "success",
      "ip_address": "192.168.1.100",
      "created_at": "2024-01-15T10:30:45.123Z"
    }
  ],
  "total": 5420,
  "page": 1,
  "per_page": 100
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Non-admin user
- `422 Unprocessable Entity`: Invalid time range (start_time > end_time)

---

## 6. Asynchronous Processing Design

### 6.1 Celery Task Architecture

#### Task: `tasks.voting.process_vote`

**Purpose**: Persist vote to PostgreSQL with transactional integrity

**Input Parameters**:
```python
@celery_app.task(bind=True, max_retries=3)
def process_vote(self, voter_id: str, candidate_id: str, booth_id: str, timestamp: str):
    """
    Process a single vote submission with retry logic.
    
    Args:
        voter_id: UUID of the voter
        candidate_id: UUID of the selected candidate
        booth_id: UUID of the polling booth
        timestamp: ISO 8601 timestamp of submission
    
    Returns:
        dict: {"status": "success", "voting_record_id": "uuid"}
    
    Raises:
        Retry: On database errors (up to 3 attempts)
    """
```

**Processing Logic**:

```python
def process_vote(self, voter_id, candidate_id, booth_id, timestamp):
    try:
        with db.session.begin():  # Begin PostgreSQL transaction
            # 1. Double-check for existing vote (unique constraint will also catch this)
            existing_vote = VotingRecord.query.filter_by(voter_id=voter_id).first()
            if existing_vote:
                raise DuplicateVoteError(f"Voter {voter_id} already voted")
            
            # 2. Create voting record
            voting_record = VotingRecord(
                id=uuid.uuid4(),
                voter_id=voter_id,
                candidate_id=candidate_id,
                booth_id=booth_id,
                voted_at=timestamp
            )
            db.session.add(voting_record)
            
            # 3. Commit transaction (unique constraint enforced here)
            db.session.commit()
        
        # 4. Log successful vote (async, outside transaction)
        audit_service.log_event(
            event_type="vote_completed",
            actor_id=voter_id,
            target_id=voting_record.id,
            outcome="success"
        )
        
        return {"status": "success", "voting_record_id": str(voting_record.id)}
    
    except IntegrityError as e:
        db.session.rollback()
        # Duplicate vote detected by unique constraint
        logger.warning(f"Duplicate vote attempt for voter {voter_id}: {e}")
        return {"status": "duplicate", "message": "Vote already recorded"}
    
    except OperationalError as e:
        db.session.rollback()
        # Database connection issue — retry with exponential backoff
        logger.error(f"Database error processing vote: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error processing vote: {e}")
        raise
```

---

### 6.2 Retry Strategy

**Configuration**:
- **Max retries**: 3 attempts
- **Backoff strategy**: Exponential (1s, 2s, 4s)
- **Retry conditions**: `OperationalError` (database connection issues)
- **No-retry conditions**: `IntegrityError` (duplicate vote — business logic error, not transient)

**Rationale**: Database connection issues are transient and often resolve within seconds. Duplicate votes are permanent constraint violations and should not be retried.

---

### 6.3 Dead-Letter Queue

**Purpose**: Capture tasks that fail after all retry attempts

**Implementation**:
- Celery's built-in dead-letter queue (Redis list: `celery_dead_letter`)
- Tasks include full payload: `{voter_id, candidate_id, booth_id, timestamp, error}`

**Operator Workflow**:
1. Admin queries dead-letter queue via Redis CLI or custom admin endpoint
2. Investigate failure reason (e.g., database constraint violation, data corruption)
3. Manually reprocess or mark as resolved

---

### 6.4 Celery Configuration

**Broker**: Redis (`redis://localhost:6379/0`)

**Result Backend**: Redis (`redis://localhost:6379/1`)

**Worker Concurrency**: Configurable via `CELERY_WORKER_CONCURRENCY` environment variable (default: 4)

**Task Routing**: Single queue (`celery`) for simplicity

**Serialization**: JSON (human-readable, debuggable)

**Task Time Limit**: 30 seconds (prevents stuck tasks)

**Example Configuration**:
```python
# tasks/celery_app.py
from celery import Celery

celery_app = Celery(
    'election_platform',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_time_limit=30,
    worker_prefetch_multiplier=1,  # Fair task distribution
)
```

---

### 6.5 Horizontal Scaling

**Scenario**: Under peak load, a single Celery worker processes 50 votes/second. To handle 500 votes/second, deploy 10 workers.

**Scaling Strategy**:
1. Launch multiple worker containers: `docker compose up --scale worker=10`
2. Each worker connects to the same Redis queue
3. Redis distributes tasks using round-robin (fair distribution)
4. PostgreSQL unique constraint prevents duplicate votes even if multiple workers process the same task

**No Additional Coordination Required**: PostgreSQL's ACID guarantees ensure correctness without distributed locks.

---

## 7. Dashboard Design

### 7.1 Plotly Dash Architecture

**Framework**: Plotly Dash (Python-native reactive web framework)

**Integration**: Runs as separate WSGI application alongside Flask API

**Authentication**: JWT-based (reuses Flask-JWT-Extended tokens)

**Access Control**: Election_Officer and Admin roles only

---

### 7.2 Dashboard Metrics

#### Overall Voter Turnout
- **Metric**: `(total_votes / total_registered_voters) * 100`
- **Source**: PostgreSQL query: `SELECT COUNT(*) FROM voting_records` and `SELECT COUNT(*) FROM voters WHERE status='active'`
- **Update Frequency**: Every 10 seconds
- **Visualization**: Large percentage display + progress bar

#### Per-Constituency Turnout
- **Metric**: Turnout % per constituency
- **Source**: JOIN `voting_records`, `voters`, `constituencies`
- **Visualization**: Bar chart sorted by turnout descending

#### Vote Distribution
- **Metric**: Votes per candidate as % of total votes in constituency
- **Source**: `SELECT candidate_id, COUNT(*) FROM voting_records WHERE constituency_id=X GROUP BY candidate_id`
- **Visualization**: Horizontal bar chart with candidate names

#### Vote Queue Depth
- **Metric**: Number of pending tasks in Redis queue
- **Source**: Celery inspect API: `celery_app.control.inspect().active_queues()`
- **Visualization**: Line graph over time + current value indicator
- **Alert**: Red indicator if queue depth > 1000

#### Processing Throughput
- **Metric**: Votes processed in last 60 seconds (rolling window)
- **Source**: Query `voting_records` with `voted_at >= NOW() - INTERVAL '60 seconds'`
- **Visualization**: Line graph with votes/second on Y-axis

#### Polling Booth Status
- **Metric**: Count of OPEN vs CLOSED booths
- **Source**: `SELECT status, COUNT(*) FROM polling_booths GROUP BY status`
- **Visualization**: Pie chart + status table

#### Celery Worker Status
- **Metric**: Active, idle, offline workers
- **Source**: Celery inspect API: `celery_app.control.inspect().active()`, `.stats()`
- **Visualization**: Status badges (green=active, yellow=idle, red=offline)
- **Alert**: Persistent red badge if any worker offline

#### PostgreSQL Connection Pool Utilization
- **Metric**: `(active_connections / max_connections) * 100`
- **Source**: SQLAlchemy engine pool stats: `db.engine.pool.size()`, `db.engine.pool.overflow()`
- **Visualization**: Gauge chart
- **Alert**: Yellow if > 70%, red if > 90%

---

### 7.3 Update Mechanism

**Implementation**: Dash callback triggered every 10 seconds

```python
@app.callback(
    [Output('turnout-metric', 'children'),
     Output('queue-depth-metric', 'children'),
     Output('worker-status', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    # Query PostgreSQL for turnout
    total_votes = db.session.query(VotingRecord).count()
    total_voters = db.session.query(Voter).filter_by(status='active').count()
    turnout = (total_votes / total_voters * 100) if total_voters > 0 else 0.0
    
    # Query Redis for queue depth
    queue_depth = celery_app.control.inspect().active_queues().get('celery', 0)
    
    # Query Celery for worker status
    stats = celery_app.control.inspect().stats()
    worker_count = len(stats) if stats else 0
    
    return f"{turnout:.2f}%", queue_depth, f"{worker_count} active"
```

---

### 7.4 Error Handling

**PostgreSQL Unavailable**:
- Display "Database Connection Lost" indicator
- Show last successfully retrieved values with staleness timestamp
- Retry connection every 10 seconds

**Redis Unavailable**:
- Display "Queue Metrics Unavailable" indicator
- Continue showing PostgreSQL-based metrics (turnout, results)

**Partial Failures**:
- Display error only for affected metric
- Do not crash entire dashboard

---

## 8. Deployment Architecture

### 8.1 Docker Compose Services

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: election_db
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "${DB_PORT:-5432}:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "${REDIS_PORT:-6379}:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    environment:
      FLASK_ENV: ${FLASK_ENV:-production}
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/election_db
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    ports:
      - "${API_PORT:-5000}:5000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    command: >
      sh -c "
        flask db upgrade &&
        gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
      "

  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/election_db
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
      CELERY_WORKER_CONCURRENCY: ${WORKER_CONCURRENCY:-4}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    command: celery -A tasks.celery_app worker --loglevel=info --concurrency=${WORKER_CONCURRENCY:-4}

  dashboard:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/election_db
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    ports:
      - "${DASHBOARD_PORT:-8050}:8050"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  locust:
    build:
      context: .
      dockerfile: docker/Dockerfile.locust
    environment:
      TARGET_HOST: http://api:5000
    ports:
      - "${LOCUST_PORT:-8089}:8089"
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

---

### 8.2 Dockerfile Examples

#### Dockerfile.api
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/

# Expose API port
EXPOSE 5000

# Run migrations and start server (overridden by docker-compose command)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

#### Dockerfile.worker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY tasks/ ./tasks/

CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info"]
```

---

### 8.3 Environment Configuration (.env.example)

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this

# Database Configuration
DB_USER=election_user
DB_PASSWORD=secure_password_change_this
DB_HOST=postgres
DB_PORT=5432
DB_NAME=election_db
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-change-this
JWT_ACCESS_TOKEN_EXPIRES=900  # 15 minutes in seconds
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 days in seconds

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_WORKER_CONCURRENCY=4

# Service Ports
API_PORT=5000
DASHBOARD_PORT=8050
REDIS_PORT=6379
LOCUST_PORT=8089

# Election Day Configuration
ELECTION_START_TIME=2024-01-15T08:00:00Z
ELECTION_END_TIME=2024-01-15T18:00:00Z
```

---

### 8.4 Startup Sequence

1. **docker compose up**
   - PostgreSQL container starts, initializes database
   - Redis container starts
   - Health checks pass

2. **API Container**
   - Waits for PostgreSQL health check
   - Runs Alembic migrations: `flask db upgrade`
   - Starts Gunicorn with 4 worker processes
   - Binds to port 5000

3. **Worker Container(s)**
   - Waits for PostgreSQL and Redis health checks
   - Starts Celery worker
   - Connects to Redis broker
   - Begins consuming tasks

4. **Dashboard Container**
   - Waits for PostgreSQL and Redis health checks
   - Starts Dash application
   - Binds to port 8050

5. **Locust Container**
   - Waits for API container
   - Starts Locust web UI
   - Binds to port 8089

**Total Startup Time**: ~15 seconds (including health checks)

---

## 9. Request Flow Examples

### 9.1 Synchronous Request Flow: Voter Registration

**Scenario**: Election officer registers a new voter

```mermaid
sequenceDiagram
    participant Officer as Election Officer
    participant API as API Endpoint<br/>(POST /api/voters)
    participant Schema as VoterSchema
    participant Service as VoterService
    participant Repo as VoterRepository
    participant DB as PostgreSQL
    participant Audit as AuditService

    Officer->>API: POST /api/voters<br/>{national_id, full_name, dob, constituency_id}
    API->>API: Validate JWT + RBAC
    API->>Schema: Validate request body
    Schema-->>API: Validated data
    API->>Service: register_voter(data)
    Service->>Repo: get_by_national_id(national_id)
    Repo->>DB: SELECT * FROM voters WHERE national_id=?
    DB-->>Repo: None (no duplicate)
    Repo-->>Service: None
    Service->>Repo: create(voter)
    Repo->>DB: INSERT INTO voters VALUES (...)
    DB-->>Repo: Voter entity
    Repo-->>Service: Voter entity
    Service->>Audit: log_event('voter_registered', actor_id, voter_id)
    Audit-->>Service: Success
    Service-->>API: Voter entity
    API-->>Officer: HTTP 201 Created<br/>{id, masked_national_id, ...}
```

**Duration**: ~50ms (typical)

---

### 9.2 Asynchronous Request Flow: Vote Submission

**Scenario**: Voter submits a vote during peak traffic

```mermaid
sequenceDiagram
    participant Voter
    participant API as API Endpoint<br/>(POST /api/votes)
    participant Service as VoteService
    participant Repo as VotingRecordRepository
    participant DB as PostgreSQL
    participant Redis as Redis Queue
    participant Worker as Celery Worker
    participant Audit as AuditService

    Voter->>API: POST /api/votes<br/>{candidate_id, booth_id}
    API->>API: Validate JWT + RBAC
    API->>Service: submit_vote(voter_id, candidate_id, booth_id)
    
    Note over Service: Pre-submission validation
    Service->>Repo: get_by_voter_id(voter_id)
    Repo->>DB: SELECT * FROM voting_records WHERE voter_id=?
    DB-->>Repo: None (no existing vote)
    Repo-->>Service: None
    
    Service->>Service: Validate candidate in constituency
    Service->>Service: Validate booth is OPEN
    
    Note over Service: Enqueue task
    Service->>Redis: Enqueue process_vote task
    Redis-->>Service: Task ID
    Service-->>API: Task ID
    API-->>Voter: HTTP 202 Accepted<br/>{task_id, status: "QUEUED"}
    
    Note over Worker: Asynchronous processing
    Worker->>Redis: Dequeue task
    Redis-->>Worker: {voter_id, candidate_id, booth_id, timestamp}
    
    Worker->>DB: BEGIN TRANSACTION
    Worker->>DB: SELECT * FROM voting_records WHERE voter_id=? FOR UPDATE
    DB-->>Worker: None
    Worker->>DB: INSERT INTO voting_records VALUES (...)
    DB-->>Worker: Success (unique constraint satisfied)
    Worker->>DB: COMMIT TRANSACTION
    
    Worker->>Audit: log_event('vote_completed', voter_id, voting_record_id)
    Worker->>Redis: Update task status to COMPLETED
    
    Note over Voter: Voter polls for status
    Voter->>API: GET /api/votes/status/{task_id}
    API->>Redis: Get task status
    Redis-->>API: COMPLETED
    API-->>Voter: HTTP 200 OK<br/>{task_id, status: "COMPLETED"}
```

**API Response Time**: ~20ms (task enqueuing only)  
**Total Processing Time**: ~200ms (including worker processing)

---

### 9.3 Concurrent Vote Scenario: Duplicate Prevention

**Scenario**: Two workers attempt to process the same vote simultaneously (edge case)

```mermaid
sequenceDiagram
    participant Worker1 as Celery Worker 1
    participant Worker2 as Celery Worker 2
    participant DB as PostgreSQL

    Note over Worker1,Worker2: Both dequeue task for voter_id=123 (race condition)
    
    par Worker 1 Processing
        Worker1->>DB: BEGIN TRANSACTION
        Worker1->>DB: INSERT INTO voting_records (voter_id=123, ...)
        DB-->>Worker1: Success
        Worker1->>DB: COMMIT TRANSACTION
    and Worker 2 Processing
        Worker2->>DB: BEGIN TRANSACTION
        Worker2->>DB: INSERT INTO voting_records (voter_id=123, ...)
        DB-->>Worker2: IntegrityError: UNIQUE constraint violation
        Worker2->>DB: ROLLBACK TRANSACTION
        Worker2->>Worker2: Log duplicate attempt, mark task as duplicate
    end
    
    Note over DB: Only ONE vote persisted<br/>Unique constraint enforced correctness
```

**Outcome**: PostgreSQL's UNIQUE constraint on `voter_id` ensures exactly one vote is recorded, even under race conditions.

---

## 10. Design Rationale

### 10.1 Why Flask Instead of FastAPI or Django?

**Flask Chosen Because**:
- Lightweight and unopinionated (suitable for modular monolith)
- Mature ecosystem with extensive documentation
- Excellent integration with SQLAlchemy and Celery
- Well-understood by interview panels and junior developers
- No unnecessary ORM overhead (Django) or async complexity (FastAPI)

**Trade-offs Accepted**:
- Manual configuration required (vs. Django's batteries-included approach)
- No built-in async/await support (Celery handles async operations)

---

### 10.2 Why SQLAlchemy ORM Instead of Raw SQL?

**SQLAlchemy Chosen Because**:
- Abstracts database-specific SQL dialects (PostgreSQL, MySQL, SQLite)
- Provides type safety and IDE autocomplete
- Integrates seamlessly with Alembic for schema versioning
- Reduces SQL injection risk through parameterized queries
- Simplifies testing with in-memory SQLite databases

**Trade-offs Accepted**:
- Slightly higher overhead than raw SQL (negligible for this scale)
- Requires learning ORM query API

---

### 10.3 Why Repository Pattern?

**Repository Pattern Chosen Because**:
- Decouples business logic from data access implementation
- Makes unit testing easier (mock repositories instead of database)
- Centralizes query logic (avoid duplicated queries across services)
- Provides single point for query optimization and caching

**Example Without Repository** (tight coupling):
```python
# service/vote_service.py (BAD)
def submit_vote(voter_id, candidate_id):
    existing_vote = db.session.query(VotingRecord).filter_by(voter_id=voter_id).first()
    if existing_vote:
        raise DuplicateVoteError()
    # ... more logic
```

**Example With Repository** (loose coupling):
```python
# service/vote_service.py (GOOD)
def submit_vote(voter_id, candidate_id):
    existing_vote = voting_record_repo.get_by_voter_id(voter_id)
    if existing_vote:
        raise DuplicateVoteError()
    # ... more logic
```

**Testing Benefit**:
```python
# tests/test_vote_service.py
def test_duplicate_vote_rejected():
    # Mock repository returns existing vote
    mock_repo = MagicMock()
    mock_repo.get_by_voter_id.return_value = VotingRecord(...)
    
    service = VoteService(mock_repo)
    with pytest.raises(DuplicateVoteError):
        service.submit_vote('voter-123', 'candidate-456')
```

---

### 10.4 Why Service Layer?

**Service Layer Chosen Because**:
- Centralizes business logic (prevents fat models and fat controllers)
- Coordinates multiple repositories (e.g., vote submission checks voters, candidates, booths)
- Enforces business rules consistently across all API endpoints
- Simplifies transaction management (service method = transaction boundary)

**Example** (vote submission orchestration):
```python
# service/vote_service.py
class VoteService:
    def __init__(self, vote_repo, voter_repo, candidate_repo, booth_repo):
        self.vote_repo = vote_repo
        self.voter_repo = voter_repo
        self.candidate_repo = candidate_repo
        self.booth_repo = booth_repo
    
    def submit_vote(self, voter_id, candidate_id, booth_id):
        # Business rule 1: Check for duplicate vote
        if self.vote_repo.get_by_voter_id(voter_id):
            raise DuplicateVoteError()
        
        # Business rule 2: Validate candidate in voter's constituency
        voter = self.voter_repo.get_by_id(voter_id)
        candidate = self.candidate_repo.get_by_id(candidate_id)
        if voter.constituency_id != candidate.constituency_id:
            raise InvalidCandidateError()
        
        # Business rule 3: Validate booth is open
        booth = self.booth_repo.get_by_id(booth_id)
        if booth.status != 'OPEN':
            raise BoothClosedError()
        
        # Enqueue task
        task = process_vote.delay(voter_id, candidate_id, booth_id)
        return task.id
```

---

### 10.5 Why Celery Instead of Direct Database Writes?

**Celery Chosen Because**:
- **Decouples API responsiveness from database latency**: API returns HTTP 202 immediately, vote is processed asynchronously
- **Handles traffic spikes gracefully**: Queue absorbs burst traffic, workers process at sustainable rate
- **Built-in retry logic**: Transient database errors are automatically retried
- **Horizontal scaling**: Add more workers to increase throughput
- **Dead-letter queue**: Failed tasks are preserved for manual review

**Without Celery** (synchronous):
- API response time = database write time (~200ms under load)
- Database connection pool exhaustion during traffic spikes
- No automatic retry on transient failures
- Difficult to scale processing independently from API

**With Celery** (asynchronous):
- API response time = task enqueue time (~20ms)
- Database load smoothed over time
- Automatic retry with exponential backoff
- Scale workers independently: `docker compose up --scale worker=10`

---

### 10.6 Why PostgreSQL Transactions Instead of Distributed Locks?

**PostgreSQL Transactions Chosen Because**:
- **ACID guarantees**: Atomicity, Consistency, Isolation, Durability built-in
- **Unique constraints**: Database enforces exactly-once semantics automatically
- **Simpler reasoning**: Single-node transaction easier to understand than distributed consensus
- **No external dependencies**: No need for Redis locks, ZooKeeper, or etcd
- **Interview-friendly**: ACID transactions are well-understood concepts

**Alternative Considered: Redis Distributed Lock**
- Requires external locking service (added complexity)
- Lock expiration and renewal logic (error-prone)
- Deadlock risks if lock not released
- Network partition scenarios require complex resolution

**Decision**: Leverage PostgreSQL's proven transactional guarantees rather than implementing distributed locking.

---

### 10.7 Why UUID Primary Keys?

**UUIDs Chosen Because**:
- **Security**: Prevents enumeration attacks (`/api/voters/1`, `/api/voters/2`, ...)
- **Privacy**: Sequential IDs leak registration order and volume
- **Distributed-friendly**: Can generate IDs without central coordination (future-proof)
- **Offline generation**: Workers can generate IDs before database insertion

**Trade-offs Accepted**:
- Larger storage (16 bytes vs 4 bytes for INT)
- Slightly slower indexing (vs sequential integers)

**Mitigation**: Use UUIDv4 (random), add indexes on foreign keys

---

### 10.8 Why Plotly Dash Instead of React Dashboard?

**Plotly Dash Chosen Because**:
- **Python-native**: Reuse backend models and database connections
- **Rapid prototyping**: Build real-time dashboards in ~100 lines of Python
- **Integrated authentication**: Reuse Flask-JWT-Extended tokens
- **No separate API**: Direct database queries from callbacks

**Alternative Considered: React + REST API**
- Requires separate frontend build pipeline
- Need to expose additional API endpoints for dashboard data
- Increased development time
- Two languages/frameworks to maintain

**Decision**: Prioritize speed and simplicity for internal-facing operations dashboard.

---

### 10.9 Why Docker Compose Instead of Kubernetes?

**Docker Compose Chosen Because**:
- **Single-command startup**: `docker compose up` starts entire platform
- **Local development parity**: Same environment on all developer machines
- **No orchestration complexity**: No need for pod management, service meshes, or ingress controllers
- **Sufficient scale**: Platform targets moderate traffic (thousands of votes/minute, not millions)

**When to Consider Kubernetes**:
- Multi-region deployment
- Auto-scaling requirements beyond `--scale worker=N`
- High-availability requirements (multi-node database clusters)

**Current Decision**: YAGNI principle — avoid premature complexity.

---

## 11. Non-Functional Considerations

### 11.1 Performance

**API Response Times** (target under normal load):
- Authentication: <50ms
- Voter registration: <100ms
- Vote submission: <30ms (enqueue only)
- Results query: <200ms (with proper indexes)

**Throughput** (target):
- Vote submissions: 500 votes/second sustained (with 10 workers)
- Dashboard updates: 10-second refresh interval

**Optimization Strategies**:
- Database indexes on foreign keys and query columns
- Connection pooling (SQLAlchemy default: 5 connections per process)
- Celery worker horizontal scaling
- Redis for low-latency task queuing

**Load Testing**:
- Locust simulations with 1,000-10,000 concurrent users
- Identify bottlenecks before election day
- Iterate on worker count, connection pool size, and query optimization

---

### 11.2 Reliability

**Duplicate Vote Prevention**:
- **Primary Mechanism**: PostgreSQL UNIQUE constraint on `voting_records.voter_id`
- **Secondary Check**: Application-level check before task enqueue
- **Concurrency Safety**: Transaction isolation ensures atomicity

**Task Retry Strategy**:
- Transient failures (database connection issues): Retry up to 3 times
- Permanent failures (constraint violations): No retry, log to dead-letter queue

**Data Persistence**:
- PostgreSQL data volume: `postgres_data` (survives container restarts)
- Redis snapshots: `redis_data` (RDB persistence enabled)

**Health Checks**:
- PostgreSQL: `pg_isready` every 10 seconds
- Redis: `redis-cli ping` every 10 seconds
- Services wait for healthy dependencies before starting

---

### 11.3 Security

**Authentication**:
- JWT access tokens (15-minute expiry, short window for token theft)
- Refresh tokens (7-day expiry, stored hashed in database)
- Logout invalidates refresh tokens (prevents reuse)

**Authorization**:
- RBAC enforced on every protected endpoint
- Decorators: `@require_role('Admin', 'Election_Officer')`
- Constituency-scoped access (Candidates can only see own results)

**Password Storage**:
- Bcrypt hashing with cost factor 12 (~250ms per hash)
- Salted hashes (unique salt per password)
- No plaintext passwords in database or logs

**Audit Logging**:
- Every security-relevant action logged (login, vote, booth status change)
- Append-only table (no UPDATE or DELETE via API)
- Includes actor, target, outcome, IP address, timestamp

**Input Validation**:
- Schema validation on all API requests (Marshmallow or Pydantic)
- Length limits on all string fields
- Type checking on all fields

**SQL Injection Prevention**:
- SQLAlchemy ORM uses parameterized queries
- No raw SQL with string interpolation

**Enumeration Prevention**:
- UUID primary keys (non-sequential)
- Generic error messages (login failure doesn't indicate if username or password is wrong)

---

### 11.4 Scalability

**Current Design Supports**:
- **Voters**: 100,000+ registered voters
- **Throughput**: 500 votes/second sustained (10 workers)
- **Concurrency**: 1,000+ concurrent API requests

**Scaling Strategies**:

1. **Horizontal Scaling — Celery Workers**
   - Command: `docker compose up --scale worker=20`
   - Linear throughput increase (20 workers = 1,000 votes/second)
   - No code changes required

2. **Database Optimization**
   - Add indexes on high-frequency query columns
   - Tune PostgreSQL settings (`shared_buffers`, `work_mem`)
   - Use read replicas for results queries (separate read/write concerns)

3. **API Scaling** (if needed beyond modular monolith):
   - Deploy multiple API containers behind load balancer
   - Session state stored in JWT (stateless API)
   - Shared PostgreSQL and Redis instances

**When to Consider Microservices**:
- Different scaling characteristics per domain (e.g., results service needs 10x more capacity than voter registration)
- Team size > 20 engineers (organizational scaling)
- Different deployment cadences per service

**Current Decision**: Modular monolith is sufficient for stated requirements. Premature microservices add complexity without current benefits.

---

### 11.5 Maintainability

**Code Organization**:
- Clear module boundaries (API, services, repositories, models)
- Single Responsibility Principle per module
- Dependency Inversion (services depend on repository interfaces, not concrete implementations)

**Testing Strategy**:
- Unit tests for services and repositories (mock database)
- Integration tests for API endpoints (test database)
- Load tests for performance validation (Locust)
- Property-based tests for critical business logic (vote processing, duplicate prevention)

**Documentation**:
- API documentation (OpenAPI/Swagger)
- Architecture decision records (ADRs) for major design choices
- Code comments for complex business logic
- README with setup instructions

**Version Control**:
- Alembic migrations for schema versioning
- Git branching strategy (feature branches, main branch protected)
- CI/CD pipeline (linting, testing, Docker build)

---

### 11.6 Deployability

**One-Command Startup**:
```bash
docker compose up
```

**One-Command Teardown**:
```bash
docker compose down -v  # Removes containers and volumes
```

**Environment Configuration**:
- All settings via `.env` file (12-factor app principle)
- No hardcoded credentials or hostnames
- Separate profiles for dev, test, production

**Database Migrations**:
- Automatic migration on API startup: `flask db upgrade`
- Rollback support: `flask db downgrade`
- Version-controlled migration scripts

**Zero-Downtime Deployments** (future):
- Blue-green deployment (run new version alongside old, switch traffic)
- Database migrations designed for backward compatibility
- Feature flags for gradual rollouts

---

## 12. Testing Strategy

### 12.1 Unit Tests

**Scope**: Services, repositories, utilities (no database)

**Tools**: pytest, unittest.mock

**Example** (service unit test):
```python
# tests/unit/test_vote_service.py
def test_duplicate_vote_rejected():
    # Arrange
    mock_vote_repo = MagicMock()
    mock_vote_repo.get_by_voter_id.return_value = VotingRecord(voter_id='voter-123')
    service = VoteService(mock_vote_repo, None, None, None)
    
    # Act & Assert
    with pytest.raises(DuplicateVoteError):
        service.submit_vote('voter-123', 'candidate-456', 'booth-789')
```

**Coverage Target**: >80% for services and repositories

---

### 12.2 Integration Tests

**Scope**: API endpoints, database interactions, Celery tasks

**Tools**: pytest, pytest-flask, testcontainers (for PostgreSQL and Redis)

**Example** (API integration test):
```python
# tests/integration/test_vote_api.py
def test_vote_submission_returns_202(client, auth_header, db_session):
    # Arrange: Create voter, candidate, booth
    voter = create_voter(db_session, national_id='123')
    candidate = create_candidate(db_session, constituency_id=voter.constituency_id)
    booth = create_booth(db_session, constituency_id=voter.constituency_id, status='OPEN')
    
    # Act: Submit vote
    response = client.post('/api/votes', 
                          json={'candidate_id': str(candidate.id), 'booth_id': str(booth.id)},
                          headers=auth_header)
    
    # Assert
    assert response.status_code == 202
    assert 'task_id' in response.json
```

**Coverage Target**: All API endpoints, happy path + error cases

---

### 12.3 Load Tests

**Scope**: Performance validation, bottleneck identification

**Tools**: Locust

**Configuration**:
- Virtual users: 1,000-10,000
- Spawn rate: 100 users/second
- Duration: 10-30 minutes

**Scenarios**:

1. **Voter Registration Burst**
   - Target: 100 registrations/second sustained
   - Success criteria: <100ms 95th percentile latency

2. **Vote Submission Peak**
   - Target: 500 votes/second sustained
   - Success criteria: <50ms API response time (enqueue), <200ms total processing time

3. **Results Query Load**
   - Target: 100 results requests/second
   - Success criteria: <200ms 95th percentile latency

**Example Locust Test**:
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class VoterUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post('/api/auth/login', json={
            'username': 'voter123',
            'password': 'password'
        })
        self.token = response.json()['access_token']
    
    @task
    def submit_vote(self):
        self.client.post('/api/votes', 
                        json={'candidate_id': 'candidate-uuid', 'booth_id': 'booth-uuid'},
                        headers={'Authorization': f'Bearer {self.token}'})
```

---

### 12.4 Property-Based Testing Assessment

**Why PBT is NOT Applied to This Feature:**

Property-based testing (PBT) is powerful for testing pure functions with universal properties across a wide input space. However, the Election Operations Platform is **NOT a good candidate for PBT** because:

1. **Infrastructure Focus**: The platform is primarily infrastructure orchestration (Docker Compose, PostgreSQL, Redis, Celery) rather than pure algorithmic logic.

2. **External Dependencies**: Most critical operations involve external services:
   - Vote processing depends on PostgreSQL transactions
   - Task queuing depends on Redis
   - Results aggregation depends on database queries
   - PBT works best for pure functions, not I/O-heavy operations

3. **CRUD-Heavy Operations**: Most API endpoints perform simple CRUD operations (create voter, update booth status, query results) which are better tested with example-based integration tests.

4. **Configuration and Setup**: Many requirements concern environment configuration, database migrations, and Docker orchestration — areas where PBT doesn't apply.

**Alternative Testing Strategies Used Instead:**

- **Unit tests with mocks**: Test business logic in services with mocked repositories
- **Integration tests**: Test complete request flows against test database
- **Load tests**: Validate performance and concurrency handling under realistic traffic
- **Schema validation tests**: Ensure database constraints enforce business rules

**Example of Why Integration Tests Are More Appropriate:**

Consider Requirement 6.1: "WHEN a Voter submits a vote... THE API_Server SHALL check that no existing Voting_Record exists... and return HTTP 202"

**Why NOT PBT**:
- Behavior involves external systems (PostgreSQL, Redis)
- Testing "for all voters" requires database state setup for each iteration
- The property isn't about input variation — it's about transaction isolation and constraint enforcement
- Running 100 iterations with database setup/teardown is expensive and slow

**Why Integration Test**:
- Setup test database once
- Test specific scenarios: first vote (succeeds), second vote (409 conflict)
- Verify PostgreSQL constraint behavior
- Fast execution (1-2 seconds total)

**Conclusion**: This feature is better served by a robust integration and load testing strategy than by property-based testing.

---

## 13. Error Handling Strategy

### 13.1 API Error Responses

**Standard Error Format**:
```json
{
  "error": {
    "code": "DUPLICATE_VOTE",
    "message": "You have already cast your vote in this election.",
    "details": {
      "voter_id": "voter-uuid",
      "existing_vote_id": "vote-uuid"
    }
  },
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

**HTTP Status Code Mapping**:
- `400 Bad Request`: Malformed request body (invalid JSON)
- `401 Unauthorized`: Missing, invalid, or expired token
- `403 Forbidden`: Insufficient role permissions
- `404 Not Found`: Resource does not exist
- `409 Conflict`: Resource conflict (duplicate vote, booth already open)
- `422 Unprocessable Entity`: Validation errors (missing fields, invalid values)
- `500 Internal Server Error`: Unexpected server errors
- `503 Service Unavailable`: External service unavailable (Redis, audit log)

---

### 13.2 Database Error Handling

**IntegrityError** (unique constraint, foreign key violations):
- Catch and convert to appropriate HTTP status (409 or 422)
- Log error with full context
- Do not expose database schema details in response

**OperationalError** (connection failures, timeouts):
- Retry transient operations (Celery tasks)
- Return 503 for API requests if database unreachable
- Log error with connection details

**Example**:
```python
# service/vote_service.py
try:
    db.session.commit()
except IntegrityError as e:
    db.session.rollback()
    if 'unique constraint' in str(e):
        raise DuplicateVoteError("Voter has already voted")
    elif 'foreign key constraint' in str(e):
        raise InvalidReferenceError("Referenced resource does not exist")
    else:
        raise
except OperationalError as e:
    db.session.rollback()
    logger.error(f"Database connection error: {e}")
    raise ServiceUnavailableError("Database temporarily unavailable")
```

---

### 13.3 Celery Task Error Handling

**Retry Strategy**:
- Transient errors (OperationalError): Retry up to 3 times with exponential backoff
- Permanent errors (IntegrityError): Do not retry, log to dead-letter queue

**Example**:
```python
@celery_app.task(bind=True, max_retries=3)
def process_vote(self, voter_id, candidate_id, booth_id, timestamp):
    try:
        # ... processing logic
        pass
    except OperationalError as e:
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except IntegrityError as e:
        logger.error(f"Permanent error processing vote: {e}")
        # Do not retry, task goes to dead-letter queue
        raise
```

---

## 14. Operational Monitoring

### 14.1 Application Logging

**Log Levels**:
- **DEBUG**: Detailed diagnostic information (disabled in production)
- **INFO**: General informational messages (user login, vote submitted)
- **WARNING**: Potential issues (high queue depth, slow queries)
- **ERROR**: Error events that still allow the application to continue
- **CRITICAL**: Serious errors requiring immediate attention

**Structured Logging** (JSON format):
```python
logger.info("Vote submitted", extra={
    "voter_id": voter_id,
    "candidate_id": candidate_id,
    "booth_id": booth_id,
    "task_id": task.id,
    "timestamp": datetime.utcnow().isoformat()
})
```

**Log Aggregation** (future):
- Export logs to centralized system (ELK stack, Splunk)
- Set up alerts for error rate thresholds
- Create dashboards for operational metrics

---

### 14.2 Metrics Exposed

**Application Metrics**:
- API request rate (requests/second)
- API response time (median, 95th percentile)
- API error rate (% of 5xx responses)

**Vote Processing Metrics**:
- Vote queue depth (tasks pending in Redis)
- Vote processing rate (votes/second)
- Vote processing errors (count, error types)

**Database Metrics**:
- Connection pool utilization (%)
- Query execution time (median, 95th percentile)
- Transaction rollback rate

**Celery Metrics**:
- Active worker count
- Task success rate (%)
- Task retry rate (%)

**Metric Collection** (future):
- Prometheus exporters for each service
- Grafana dashboards for visualization
- Alerting rules for threshold breaches

---

### 14.3 Health Check Endpoints

#### GET /api/health

**Description**: Application health check

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "celery_workers": "healthy"
  }
}
```

**Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "checks": {
    "database": "unhealthy",
    "redis": "healthy",
    "celery_workers": "degraded"
  }
}
```

**Check Logic**:
```python
# api/health.py
@api.route('/health')
def health_check():
    checks = {}
    
    # Database check
    try:
        db.session.execute('SELECT 1')
        checks['database'] = 'healthy'
    except Exception:
        checks['database'] = 'unhealthy'
    
    # Redis check
    try:
        redis_client.ping()
        checks['redis'] = 'healthy'
    except Exception:
        checks['redis'] = 'unhealthy'
    
    # Celery worker check
    stats = celery_app.control.inspect().stats()
    if stats and len(stats) > 0:
        checks['celery_workers'] = 'healthy'
    else:
        checks['celery_workers'] = 'unhealthy'
    
    overall_status = 'healthy' if all(v == 'healthy' for v in checks.values()) else 'unhealthy'
    status_code = 200 if overall_status == 'healthy' else 503
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'checks': checks
    }), status_code
```

---

## 15. Security Considerations

### 15.1 Threat Model

**Threats Addressed**:

1. **Unauthorized Access**
   - Mitigation: JWT authentication + RBAC on all protected endpoints
   - Detection: Audit logs record all 401/403 responses

2. **Duplicate Voting**
   - Mitigation: PostgreSQL unique constraint on `voter_id` + application-level check
   - Detection: Audit logs record duplicate vote attempts

3. **Credential Theft**
   - Mitigation: Short-lived access tokens (15 minutes), bcrypt password hashing (cost 12)
   - Detection: Monitor for unusual login patterns (e.g., multiple logins from different IPs)

4. **SQL Injection**
   - Mitigation: SQLAlchemy ORM uses parameterized queries (no raw SQL with string interpolation)
   - Detection: Log all database errors

5. **Enumeration Attacks**
   - Mitigation: UUID primary keys (non-sequential), generic error messages
   - Detection: Rate limiting on login endpoint (future)

6. **Data Tampering**
   - Mitigation: Append-only audit log, foreign key constraints with ON DELETE RESTRICT
   - Detection: Audit log integrity checks (future)

---

### 15.2 Authentication Flow Security

**Token Lifecycle**:

1. **Login** (`POST /api/auth/login`):
   - User submits username + password
   - Server verifies bcrypt hash (cost factor 12, ~250ms)
   - Server generates access token (15-minute expiry) + refresh token (7-day expiry)
   - Refresh token hash stored in database

2. **API Request** (protected endpoints):
   - Client includes `Authorization: Bearer <access_token>` header
   - Flask-JWT-Extended validates token signature + expiry
   - RBAC decorator checks user role
   - Request proceeds if authorized

3. **Token Refresh** (`POST /api/auth/refresh`):
   - Client submits refresh token
   - Server validates token signature + expiry
   - Server checks if token is invalidated (logout flag in database)
   - Server issues new access token + new refresh token
   - Old refresh token invalidated

4. **Logout** (`POST /api/auth/logout`):
   - Server marks refresh token as invalidated in database
   - Future refresh attempts fail with 401

**Security Properties**:
- Access tokens are short-lived (limit exposure window)
- Refresh tokens are long-lived but revocable (balance convenience + security)
- Token theft requires both access token AND refresh token to maintain long-term access
- Logout invalidates refresh tokens (forced re-authentication)

---

### 15.3 Password Security

**Storage**:
- Bcrypt hashing with cost factor 12 (~250ms per hash)
- Unique salt per password (automatic with bcrypt)
- No plaintext passwords in database, logs, or error messages

**Complexity Requirements** (enforced at API level):
- Minimum 8 characters
- Maximum 128 characters (prevents long-password DoS)
- No specific complexity rules (NIST recommendations: length > complexity)

**Future Enhancements**:
- Password breach detection (check against haveibeenpwned.com API)
- Multi-factor authentication (TOTP)
- Password expiry policies (configurable per role)

---

## 16. Future Enhancements

### 16.1 Phase 2 Features (Post-MVP)

**Real-Time Notifications**:
- WebSocket support for live dashboard updates (replace 10-second polling)
- Push notifications for election officers (booth issues, queue depth alerts)

**Advanced Analytics**:
- Historical turnout trends (compare to previous elections)
- Predictive models for turnout forecasting
- Anomaly detection (unusual voting patterns)

**Multi-Election Support**:
- Run multiple elections simultaneously
- Election-specific configurations (start/end times, constituencies)
- Historical election data archival

**Enhanced Audit Trail**:
- Blockchain-based audit log (immutable, tamper-proof)
- Cryptographic signatures on voting records
- Voter receipt generation (anonymized confirmation)

**Geographic Visualization**:
- Map-based constituency visualization
- Real-time turnout heatmap
- Booth location mapping

---

### 16.2 Scalability Enhancements

**Database Scaling**:
- Read replicas for results queries (separate read/write traffic)
- Partitioning on `voting_records` by constituency (improved query performance)
- Materialized views for pre-aggregated results

**Caching Layer**:
- Redis cache for frequently accessed data (constituency lists, candidate lists)
- Cache invalidation strategy (time-based + event-based)

**CDN Integration**:
- Static asset delivery (dashboard JavaScript/CSS)
- Reduce load on origin servers

**Multi-Region Deployment**:
- Deploy API servers in multiple regions (reduce latency for geographically distributed booths)
- PostgreSQL replication across regions (disaster recovery)

---

### 16.3 Operational Enhancements

**Observability**:
- Distributed tracing (OpenTelemetry) for request flow visibility
- Application performance monitoring (APM) integration
- Alerting rules for SLA violations

**Chaos Engineering**:
- Simulate database failures (test retry logic)
- Simulate network partitions (test resilience)
- Simulate traffic spikes (test auto-scaling)

**Blue-Green Deployments**:
- Zero-downtime deployments
- Instant rollback capability
- Database migration compatibility checks

---

## 17. Design Compliance Matrix

### 17.1 Requirements Traceability

| Requirement | Design Component | Implementation Notes |
|------------|------------------|---------------------|
| Req 1: User Authentication | `app/auth/jwt_manager.py`, `POST /api/auth/login` | JWT access + refresh tokens, bcrypt hashing |
| Req 2: RBAC | `app/auth/decorators.py`, `@require_role` | Role-based access control on all protected endpoints |
| Req 3: Voter Registration | `POST /api/voters`, `VoterService`, `VoterRepository` | Unique national_id constraint, audit logging |
| Req 4: Candidate Registration | `POST /api/candidates`, `CandidateService` | Maximum 20 candidates per constituency |
| Req 5: Polling Booth Management | `POST /api/booths`, `PATCH /api/booths/{id}/open` | Status transitions with election window validation |
| Req 6: Vote Submission | `POST /api/votes`, `tasks.voting.process_vote` | Asynchronous processing, duplicate prevention |
| Req 7: Vote Processing Pipeline | Celery workers, PostgreSQL transactions | FIFO queue, unique constraint enforcement |
| Req 8: Election Results | `GET /api/results/{constituency_id}`, `ResultsService` | Indexed queries, aggregate counts |
| Req 9: Operations Dashboard | Plotly Dash, `dashboard/app.py` | 10-second refresh, JWT authentication |
| Req 10: Audit Logging | `AuditLog` model, `AuditService` | Append-only table, asynchronous writes |
| Req 11: Load Simulation | Locust, `tests/load/locustfile.py` | Configurable parameters, metrics reporting |
| Req 12: Configuration Management | `app/config/settings.py`, `.env` file | Environment variables, 12-factor app |
| Req 13: Containerized Deployment | Docker Compose, `docker/docker-compose.yml` | Single-command startup, automatic migrations |
| Req 14: Database Schema Integrity | PostgreSQL constraints, Alembic migrations | UUID PKs, foreign keys, unique constraints |

---

## 18. Conclusion

The Election Operations Platform is designed as a **modular monolith** to balance simplicity, maintainability, and scalability. The architecture leverages proven technologies (Flask, PostgreSQL, Celery, Redis) and design patterns (Repository, Service Layer, RBAC) to deliver a production-quality system that:

- **Prevents duplicate votes** through PostgreSQL unique constraints and transactional guarantees
- **Maintains API responsiveness** through asynchronous vote processing with Celery
- **Provides operational visibility** through a real-time Plotly Dash dashboard
- **Validates performance** through built-in Locust load simulation
- **Ensures security** through JWT authentication, RBAC, bcrypt password hashing, and audit logging
- **Simplifies deployment** through Docker Compose single-command startup

The design prioritizes **KISS (Keep It Simple)** and **YAGNI (You Aren't Gonna Need It)** principles, avoiding unnecessary complexity like microservices, distributed locks, or premature optimization. All architectural decisions are justified by specific requirements and engineering constraints, making the system interview-friendly and maintainable.

**Next Steps**:
1. Implement database models and migrations (Alembic)
2. Build repository layer with unit tests
3. Implement service layer with business logic
4. Develop API endpoints with integration tests
5. Build Celery tasks with retry logic
6. Create Plotly Dash dashboard
7. Set up Docker Compose environment
8. Conduct load testing and performance tuning
9. Deploy to production environment

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Author**: Election Operations Platform Team  
**Status**: Approved for Implementation
