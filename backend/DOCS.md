# MillDash Backend Documentation

## Overview
MillDash backend is a robust FastAPI-based service for managing industrial maintenance operations. It provides RESTful APIs for ticket management, user authentication, analytics, inventory control, and real-time event dispatching. The backend is modular, type-annotated, and thoroughly commented for maintainability and clarity.

---

## Directory Structure

- **main.py**: FastAPI application entry point; includes router registration and startup logic.
- **database_models.py**: SQLAlchemy ORM models for all database tables (tickets, users, components, etc.).
- **database.py**: Database session management and engine setup.
- **database_utils.py**: Utility functions for database operations (CRUD helpers, migrations).
- **schemas.py**: Pydantic models for request/response validation and serialization.
- **security.py**: Authentication, password hashing, JWT token management.
- **event_dispatcher.py**: Real-time event handling (WebSocket, MQTT integration).
- **websocket_manager.py**: WebSocket connection management and broadcast logic.
- **ingestor.py**: Data ingestion utilities for historical and live data.
- **const/config.py**: Centralized configuration (env vars, constants).
- **routers/**: API route modules, each focused on a domain:
  - **auth.py**: User authentication and registration endpoints.
  - **dashboard_optimized.py**: Optimized dashboard analytics endpoints.
  - **events.py**: Event logging and dispatch endpoints.
  - **fourjaw_proxy.py**: Proxy endpoints for FourJaw integration.
  - **inventory.py**: Inventory management endpoints.
  - **maintenance.py**: Maintenance ticket endpoints.
  - **production.py**: Production data endpoints.
  - **websocket.py**: WebSocket API endpoints.
- **services/**: Business logic modules:
  - **analytics_service.py**: Analytics and reporting logic.
  - **background_service.py**: Background tasks and schedulers.
  - **base_service.py**: Shared service utilities.
  - **machine_service.py**: Machine data and status logic.
  - **maintenance_service.py**: Maintenance ticket business logic.
  - **production_service.py**: Production data business logic.
  - **user_service.py**: User management and authentication logic.
- **scripts/**: Utility scripts for data loading and test user creation.
- **data/**: SQLite database and CSV data files.
- **uploads/**: Directory for uploaded ticket images.
- **requirements.txt**: Python dependencies.
- **Dockerfile, docker-compose.yml**: Containerization and orchestration configs.

---

## Key Technologies
- **FastAPI**: High-performance web framework for REST APIs.
- **SQLAlchemy**: ORM for database modeling and queries.
- **Pydantic**: Data validation and serialization.
- **WebSocket & MQTT**: Real-time event dispatching and machine integration.
- **APScheduler**: Background task scheduling.
- **httpx, pandas**: HTTP requests and data analysis utilities.

---

## Main Modules & Features

### main.py
- Initializes FastAPI app, includes all routers, sets up CORS, and configures startup/shutdown events.
- Logs all startup, shutdown, and error events with detailed context.

### database_models.py
- Defines all database tables as SQLAlchemy models.
- Includes verbose comments for each model and field.
- Type annotations for all columns and relationships.

### database.py & database_utils.py
- Manages database engine, sessions, and connection pooling.
- Utility functions for CRUD operations, migrations, and error handling.
- Logs all database connections, queries, and errors with full context.

### schemas.py
- Pydantic models for request/response validation.
- Explicit type annotations and field descriptions.
- Used for all API endpoints to ensure data integrity.

### security.py
- Handles password hashing, JWT token creation/validation, and user authentication.
- Logs all authentication attempts, failures, and token events.

### event_dispatcher.py & websocket_manager.py
- Manages real-time event dispatching via WebSocket and MQTT.
- Handles connection lifecycle, broadcasts, and error events.
- Logs all connection events, broadcasts, and errors with timestamps and user context.

### ingestor.py
- Utilities for ingesting historical and live data into the database.
- Logs all ingestion events, errors, and data sources.

### const/config.py
- Centralized configuration for environment variables, constants, and settings.
- Logs all config loads and changes.

### routers/
- Each router module provides RESTful endpoints for a specific domain.
- All endpoints are type-annotated, thoroughly commented, and log every request, response, and error with full context (user, timestamp, payload).
- Example: `maintenance.py` provides endpoints for ticket creation, update, status change, and logs all actions.

### services/
- Business logic modules for analytics, machine status, maintenance, production, and user management.
- All service methods are type-annotated and include verbose comments.
- Logs all service calls, results, and errors with full context.

### scripts/
- Utility scripts for data loading and test user creation.
- Logs all script actions, data processed, and errors.

---

## Logging & Monitoring
- All modules include thorough logging using Python's logging module.
- Logs include timestamps, user context, request/response payloads, error details, and system state.
- Startup, shutdown, API calls, database queries, authentication events, and background tasks are all logged.
- Logs are written to console and optionally to file (configurable in `const/config.py`).
- Example log entry:
  ```
  [2025-09-02 14:23:01] [INFO] [maintenance.py] Ticket #123 created by user 'alice' (payload: {...})
  [2025-09-02 14:23:02] [ERROR] [database_utils.py] DB connection failed: timeout (user: 'alice', details: {...})
  ```

---

## API Endpoints
- All endpoints are documented with request/response schemas, status codes, and error messages.
- See individual router files for endpoint details and example payloads.

---

## Type Safety & Comments
- All functions, classes, and models use explicit type annotations.
- Verbose file-level and inline comments throughout for maintainability and clarity.

---

## Extending & Customizing
- Add new features by creating new routers and services, following established patterns for type safety, comments, and logging.
- Update `schemas.py` for new request/response models.
- Add new database models in `database_models.py` and migrations in `database_utils.py`.

---

## Testing
- Backend tests are located in `tests/` and use pytest.
- All business logic and API endpoints should be covered by tests for reliability.

---

## Deployment & Operations
- Containerized using Docker and orchestrated with docker-compose.
- Environment variables and secrets managed via `.env` and `const/config.py`.
- Logs and monitoring can be integrated with external systems (e.g., ELK stack).

---

## Contribution Guidelines
- Follow Python and FastAPI best practices.
- Maintain explicit type annotations and verbose comments.
- Ensure all new features are covered by tests and include thorough logging.

---

## Contact & Support
For questions, feature requests, or bug reports, please contact the repository owner or open an issue on GitHub.

---

This documentation covers the backend. For frontend details, see `frontend/DOCS.md`.
