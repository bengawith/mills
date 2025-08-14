# Mill Dash: Production Monitoring Dashboard

## 1. Project Overview

**Mill Dash** is a secure, real-time production monitoring dashboard built for CSS Support Systems. The application provides deep, actionable insights into factory performance by visualizing data from the FourJaw manufacturing analytics platform.

The primary goal is to move from reactive problem-solving to proactive, data-driven management by offering a "single source of truth" for the factory floor. The dashboard focuses on key metrics like Overall Equipment Effectiveness (OEE), machine utilization, and provides powerful tools for analyzing performance trends across different shifts and days to identify and rectify recurring issues.

---

## 2. Solution Architecture

The project is architected as a modern, containerized web application with a clear separation between the frontend and backend services.

### Backend
* **Framework:** **FastAPI** (Python)
* **Purpose:** To provide a secure, high-performance REST API. It acts as a middle layer that fetches data from the PostgreSQL database (populated by the `ingestor` service), processes it into meaningful insights, and serves it to the frontend. The integration with the external FourJaw API is currently a placeholder for future real-time data.
* **Key Features:**
    * **Secure Authentication:** Implements token-based authentication using JWT to protect all data endpoints.
    * **Data Processing:** Contains robust logic to calculate metrics like OEE, utilization, and tag data by shift and day for trend analysis.
    * **Service Integration:** Currently processes data ingested into the local database. Future plans include direct communication with the external FourJaw API for real-time data.
* **Database:** **PostgreSQL**, managed via Docker Compose. It stores historical production data ingested from CSV files and is intended to store user data, application settings, and future historical data snapshots from the FourJaw API.

### Frontend
* **Framework:** **React** with **TypeScript** and **Vite** for a fast, modern development experience.
* **Styling:** **Tailwind CSS** combined with **shadcn/ui** and **recharts** for a professional, data-dense, and component-based design.
* **Purpose:** To provide an interactive and intuitive user interface for visualizing the complex production data served by the backend.
* **Key Features:**
    * Secure login page that communicates with the backend's token endpoint.
    * A main dashboard view with a variety of chart components (bar, pie, radial, timeline) inspired by the provided examples.
    * Global interactive filters for time range, shift, and machine selection.

### Containerization
* **Technology:** **Docker** and **Docker Compose**
* **Purpose:** To create a consistent, isolated, and reproducible environment for all four services (backend, frontend, database, and data ingestor). This ensures that the application runs the same way on any developer's machine and in production, simplifying setup and deployment.

---

## 3. Core Functionality & User Stories

* **As a Production Manager, I want to:**
    * See the real-time status of all machines on a single screen to quickly identify issues.
    * Analyze the OEE and utilization of the factory for the current day and shift.
    * Compare the performance of the Day Shift vs. the Night Shift to identify patterns.
    * Drill down into downtime reasons to understand the most common causes of production loss.
* **As a Team Leader, I want to:**
    * Be immediately notified of excessive downtime on any machine.
    * Use the dashboard in daily stand-up meetings to review the previous shift's performance.

---

## 4. Local Setup and Installation

**Prerequisites:**
* Docker
* Docker Compose

**Steps:**

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd mill-dash
    ```

2.  **Create Environment File:**
    Create a `.env` file in the root `mill-dash` directory by copying the example.
    ```bash
    # (If an example file exists)
    cp .env.example .env
    ```
    Populate the `.env` file with the necessary environment variables:
    ```
    # backend/.env
    FOURJAW_API_KEY=your_fourjaw_api_key_here
    SECRET_KEY=a_long_random_secret_key_for_jwt
    
    # docker-compose.yml
    POSTGRES_DB=mill_dash_db
    POSTGRES_USER=admin
    POSTGRES_PASSWORD=your_secure_password
    POSTGRES_HOST=db
    ```

3.  **Build and Run Containers:**
    From the root `mill-dash` directory, run:
    ```bash
    docker-compose up --build
    ```
    The `ingestor` service will automatically run and ingest CSV data into the database upon startup.

4.  **Access the Application:**
    * **Frontend:** Open your browser to `http://localhost:3000`
    * **Backend API Docs:** Open your browser to `http://localhost:8000/docs`

---

## 5. Key Files and Directories

* `docker-compose.yml`: Defines and orchestrates the multi-container application (frontend, backend, db, ingestor).
* `backend/`: Contains the FastAPI application.
    * `main.py`: The main entry point for the API, responsible for setting up middleware and including routers.
    * `routers/`: Contains the API endpoint logic, separated into `auth.py` and `data.py`.
    * `security.py`: Handles all authentication logic, including password hashing and JWT creation.
    * `models.py`: Defines the Pydantic data models for request/response validation.
    * `database.py`: Defines the SQLAlchemy engine, session, and database models (e.g., `MillData`).
    * `ingestor.py`: Script responsible for ingesting historical data from CSV files into the PostgreSQL database.
    * `fourjaw/`: Contains the logic for interacting with the FourJaw API (`api.py`) and processing its data (`data_processor.py`).
    * `const/`: Contains application configuration (`config.py`).
    * `scripts/`: Contains utility scripts, such as `create_test_user.py` and `load_historical_data.py`.
* `data/`: Contains CSV files used by the `ingestor` service to populate the PostgreSQL database with historical production data.
* `frontend/`: Contains the React application.
    * `src/App.tsx`: The main component that handles routing between the login and dashboard pages.
    * `src/pages/`: Contains the main page components (`LoginPage.tsx`, `DashboardPage.tsx`).
    * `src/components/`: Contains reusable UI components, primarily from `shadcn/ui`.
    * `src/context/`: Contains the React Context for global state management (`AuthContext.tsx`).
    * `src/lib/`: Contains utility functions (`utils.ts`) and the frontend API client (`api.ts`).

---

## 6. Future Development Roadmap

* **Real-Time Data:** Integrate WebSockets or polling to provide live updates on the dashboard, potentially by integrating directly with the FourJaw API.
* **Database Integration:** The PostgreSQL database currently stores historical data ingested from CSVs. Future work may involve optimizing data storage, adding more data types, and integrating directly with the FourJaw API for historical data.
* **User Management:** Expand the user system with different roles (e.g., Admin, Manager, Operator) and permissions, managed via a dedicated admin interface.
* **Advanced Analytics:** Add more complex charts and filters based on direct user feedback after the initial launch.
* **Mobile Responsiveness:** Develop a mobile-friendly layout for on-the-go monitoring.

