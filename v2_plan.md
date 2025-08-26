# Mill Dash v2 - Proposed Development Plan

This document outlines a proposed plan for the next version of the Mill Dash application. It includes an analysis of the current design, identifies flaws, and suggests new features and improvements.

## 1. Design Flaws and Improvements

### 1.1. Backend

#### 1.1.1. Heavy Data Processing in API Endpoints

*   **Flaw:** The `/api/v1/dashboard/analytical-data` endpoint performs heavy data processing and merging using pandas on every request. This is inefficient, not scalable, and leads to slow response times.
*   **Recommendation:** Implement a data pipeline or a background task (e.g., using Celery or APScheduler) to pre-process and aggregate the data from FourJaw, production runs, and maintenance tickets. The processed data should be stored in a new set of summary tables in the database. The API endpoint should then query these summary tables directly, which will be much faster.

#### 1.1.2. Configuration Management

*   **Flaw:** Configuration variables, such as machine IDs and CORS origins, are hardcoded in `const/config.py`.
*   **Recommendation:** Move all configuration to environment variables using a library like `python-dotenv`. This will make the application more secure and easier to configure for different environments (development, staging, production).

#### 1.1.3. Lack of a Service Layer

*   **Flaw:** The API routers contain business logic and directly query the database. This makes the code harder to test and maintain.
*   **Recommendation:** Introduce a service layer that encapsulates the business logic. The routers should call the service layer, which in turn interacts with the database. This will improve the separation of concerns and make the codebase more modular and testable.

#### 1.1.4. Lack of Automated Tests

*   **Flaw:** The project lacks a comprehensive suite of automated tests.
*   **Recommendation:** Implement unit and integration tests for the backend using `pytest`. This should include tests for the API endpoints, the service layer, and the data models.

### 1.2. Frontend

#### 1.2.1. Overuse of the `any` Type

*   **Flaw:** There are many instances of the `any` type in the frontend codebase, which undermines the benefits of using TypeScript.
*   **Recommendation:** Replace the `any` type with more specific types and interfaces. This will improve type safety, code completion, and the overall maintainability of the code.

#### 1.2.2. Lack of Automated Tests

*   **Flaw:** The frontend lacks automated tests.
*   **Recommendation:** Implement unit and component tests for the frontend using a testing framework like Jest and React Testing Library. This will ensure the reliability of the UI components and business logic.

## 2. New Feature Suggestions

### 2.1. Real-time Updates with WebSockets

*   **Description:** Instead of relying on polling, implement WebSockets to provide real-time updates on the dashboard and other pages. This will provide a much better user experience and reduce the load on the server.
*   **Implementation:** Use FastAPI's WebSocket support on the backend and a library like `socket.io-client` on the frontend.

### 2.2. Role-Based Access Control (RBAC)

*   **Description:** The `User` model already has a `role` field. This can be expanded into a full-featured RBAC system to control access to different parts of the application based on user roles (e.g., Admin, Manager, Operator).
*   **Implementation:** Create a permissions system on the backend and enforce it using FastAPI dependencies. On the frontend, conditionally render UI elements based on the user's role.

### 2.3. Advanced Inventory Management

*   **Description:** Expand the existing `RepairComponent` model into a full-featured inventory management module. This could include features like tracking stock levels, setting reorder points, and managing suppliers.
*   **Implementation:** Create new database models for suppliers and purchase orders. Build new API endpoints and frontend pages for managing the inventory.

### 2.4. Reporting and Data Export

*   **Description:** Add a reporting feature that allows users to generate and export reports on various aspects of the production process, such as OEE, utilization, and maintenance.
*   **Implementation:** Use a library like `Jinja2` to create HTML templates for the reports and a library like `WeasyPrint` to convert them to PDF. The reports could also be exported as CSV files.

### 2.5. User Notifications

*   **Description:** Implement a notification system to alert users about important events, such as new maintenance tickets, low stock levels, or production run completions.
*   **Implementation:** Create a notification model in the database and a WebSocket-based notification system to push notifications to the frontend in real-time.
