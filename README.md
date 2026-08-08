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

✨ Core Features🔐 Authentication & SecurityJWT authenticationAccess-token handlingRefresh-token storage and invalidationPassword hashing using PasslibRole-based authorizationRate limiting supportSecurity-oriented audit logging🗳️ Election OperationsConstituency managementCandidate managementVoter managementPolling-booth managementVote submission pipelineDuplicate/idempotent vote-request protectionElection-integrity validationVoting-record persistenceElection-result retrieval⚙️ Asynchronous ProcessingVote-processing operations are designed to support asynchronous background execution using:ARQRedisAsync SQLAlchemyPostgreSQLThis allows request handling and background processing to remain separated.📋 Audit & ComplianceThe platform maintains audit information for security-sensitive operations, including:Event typeActorTargetOutcomeIP addressTimestamp📊 DashboardThe project includes a dashboard layer using:DashPlotlyfor election-related analytics and visualization.🗄️ DatabaseThe platform uses PostgreSQL with SQLAlchemy 2.0's asynchronous ORM.Main Tablesusersconstituenciesvoterscandidatespolling_boothsvoting_recordsaudit_logsrefresh_tokensEntity RelationshipsConstituency - └── Voters└── Candidates└── Polling BoothsVoter - └── Voting RecordsCandidate - └── Voting RecordsPolling Booth - └── Voting RecordsUser - └── Candidates└── Voters└── Audit Logs└── Refresh TokensVoting records maintain relationships to voters, candidates, and polling booths while enforcing database-level foreign-key integrity.🔄 Database Migration HistoryThe final migration chain is:Plaintext20577bf67e5c
│
▼
002_performance_indexes
│
▼
917949da489c
│
HEAD
The initial migration establishes the application schema.The performance migration adds composite indexes for frequently accessed election-domain queries.The final migration represents the FastAPI/async migration state.Apply the complete migration chain:Bashalembic upgrade head
Check the current migration:Bashalembic current
Display migration history:Bashalembic history
🧪 TestingThe project contains automated unit, integration, domain, API, reliability, and performance-oriented tests.Run the complete test suite:Bashpytest tests/ -v
Run the performance test suite:Bashpytest tests/performance/ -v
Run coverage analysis:Bashpytest --cov=app --cov-report=xml --cov-report=term-missing tests/
The test suite covers:API latencyDatabase persistenceElection integrityVote submission pipelineWorker scalingSystem capacity under increasing workloadsAPI health checksDomain access behaviorVoting-service initializationBackground vote-processing executionThe final local test suite successfully completed: 11 passed🔍 Code QualityThe project uses automated static-analysis and security-oriented tools including:Blackisortmypyflake8Banditpip-auditRun the critical Flake8 checks:Bashflake8 app/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
Run the complete Flake8 check:Bashflake8 app/ tests/
Check Git whitespace errors:Bashgit diff --check
🐳 DockerThe project includes Docker configuration for containerized application validation.Build the application image:Bashdocker compose build
Start the services:Bashdocker compose up
Stop the services:Bashdocker compose down
Docker build and Compose configuration are also validated through the CI pipeline.🔁 CI/CD PipelineGitHub Actions automatically validates repository changes.The CI pipeline performs:PlaintextRepository Change
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
The pipeline validates that:Application code passes lintingAutomated tests passCoverage is generatedDatabase-related functionality remains validDocker configuration builds successfullyCompose configuration remains validThe final CI pipeline has been successfully validated through GitHub Actions.📦 RequirementsMajor dependencies include:FastAPIUvicornSQLAlchemyasyncpgpsycopgAlembicARQRedisPydanticPydantic SettingsPyJWTPasslibbcryptSlowAPIDashPlotlypytestpytest-asynciopytest-covhttpxBlackisortmypyflake8Banditpip-auditInstall dependencies:Bashpip install -r requirements.txt
⚙️ Local Setup1. Clone the repositoryBashgit clone [https://github.com/sa-99nje-ev/election-operations-platform.git](https://github.com/sa-99nje-ev/election-operations-platform.git)
cd election-operations-platform
2. Create a virtual environmentBashpython -m venv .venv
3. Activate the virtual environmentPowerShell:PowerShell.venv\Scripts\Activate.ps1
4. Install dependenciesBashpip install -r requirements.txt
5. Configure environment variablesCreate a .env file containing the required application configuration:Code snippetDATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/election_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secure-secret-key
Note: Do not commit credentials or secrets to the repository.6. Apply database migrationsBashalembic upgrade head
7. Start the FastAPI applicationBashuvicorn app.main:app --reload
The API will be available at http://localhost:8000FastAPI's interactive documentation is available at http://localhost:8000/docs📁 Project StructurePlaintextelection-operations-platform/
│
├── app/
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
│   ├── services/
│   │   └── ...
│   │
│   ├── workers/
│   │   └── voting_worker.py
│   │
│   ├── database.py
│   └── ...
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
├── locustfile.py
├── requirements.txt
├── pytest.ini
└── README.md
🔒 Security ConsiderationsThe application incorporates several security mechanisms:Password hashingJWT-based authenticationRefresh-token invalidationRole-based authorizationDatabase foreign-key constraintsRequest idempotencyAudit loggingRate limitingInput validation through PydanticDependency vulnerability scanningStatic security analysis📈 Performance ConsiderationsThe backend uses asynchronous components throughout the primary request and database-processing path.Performance-oriented design decisions include:Async FastAPI endpointsAsync SQLAlchemy sessionsPostgreSQL connection poolingIndexed foreign-key and lookup columnsComposite database indexesARQ background workersRedis-backed asynchronous task processingDatabase-level integrity constraintsAutomated worker-scaling tests🧩 Technology StackCategoryTechnologyBackendFastAPIServerUvicornDatabasePostgreSQLORMSQLAlchemy 2.0PostgreSQL Driverasyncpg / psycopgMigrationsAlembicBackground JobsARQMessage / Cache LayerRedisValidationPydanticAuthenticationJWTPassword HashingPasslib / bcryptRate LimitingSlowAPIDashboardDashVisualizationPlotlyTestingpytestAsync Testingpytest-asyncioHTTP TestingHTTPXCoveragepytest-covFormattingBlackImport SortingisortType CheckingmypyLintingflake8Security AnalysisBanditDependency Auditingpip-auditContainerizationDockerCI/CDGitHub Actions📜 LicenseSee the repository license file for licensing information.👤 Authorsa-99nje-ev GitHub: sa-99nje-ev🚀 Project StatusFinal Version The final implementation has been validated locally and through GitHub Actions.
