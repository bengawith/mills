# Mill Dash

Mill Dash is a comprehensive production dashboard for CSS Support Systems. It provides real-time monitoring, data analysis, and maintenance tracking for milling machines.

## Features

*   **Real-time Dashboards:** Monitor machine utilization, OEE, and downtime in real-time.
*   **Maintenance Ticketing:** Log and manage maintenance tickets for machines.
*   **Operator Terminal:** A dedicated interface for machine operators.
*   **User Authentication:** Secure user authentication and authorization.
*   **Data Ingestion:** Real-time data ingestion from machines via MQTT.

## Technologies Used

### Backend

*   **Framework:** FastAPI
*   **Database:** PostgreSQL
*   **ORM:** SQLAlchemy with Alembic for migrations
*   **Real-time:** Mosquitto (MQTT Broker) and Paho MQTT client
*   **Authentication:** JWT (JSON Web Tokens)
*   **Containerization:** Docker

### Frontend

*   **Framework:** React
*   **Build Tool:** Vite
*   **Language:** TypeScript
*   **UI Framework:** Shadcn UI with Radix UI and Tailwind CSS
*   **Routing:** React Router
*   **State Management:** React Query
*   **Containerization:** Docker with Nginx

## Project Structure

```
mill_dash/
├── backend/            # FastAPI backend application
│   ├── routers/        # API endpoint routers
│   ├── models/         # SQLAlchemy database models
│   ├── schemas/        # Pydantic data schemas
│   ├── ingestor.py     # MQTT data ingestor
│   └── ...
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── pages/      # Application pages
│   │   ├── components/ # Reusable components
│   │   ├── lib/        # Utility functions and API client
│   │   └── ...
│   └── ...
├── data/               # Data files (e.g., CSVs)
├── docker-compose.yml  # Docker Compose configuration
└── .env.example        # Example environment variables
```

## Getting Started

### Prerequisites

*   Docker
*   Docker Compose

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd mill_dash
    ```

2.  **Create an environment file:**
    Copy the `.env.example` file to a new file named `.env` and update the environment variables as needed.
    ```bash
    cp .env.example .env
    ```

### Running the Application

1.  **Build and start the services:**
    ```bash
    docker-compose up --build
    ```

2.  **Access the application:**
    *   **Frontend:** `http://localhost:3000`
    *   **Backend API:** `http://localhost:8000/docs`

## API Endpoints

The backend API provides the following endpoints:

*   `/auth`: User authentication and registration.
*   `/data`: Data-related endpoints.
*   `/production`: Production-related endpoints.
*   `/maintenance`: Maintenance ticketing endpoints.
*   `/inventory`: Inventory management endpoints.
*   `/events`: Event tracking endpoints.
*   `/fourjaw_proxy`: Proxy for the FourJaw API.
*   `/dashboard`: Dashboard data endpoints.

For a detailed API documentation, visit `http://localhost:8000/docs` after starting the application.

## Frontend Pages

The frontend application includes the following pages:

*   **Login/Register:** User authentication pages.
*   **Dashboard:** Real-time monitoring of machine data.
*   **Maintenance Hub:** View and manage maintenance tickets.
*   **Log New Ticket:** Create a new maintenance ticket.
*   **Manage Tickets:** A detailed view for managing individual tickets.
*   **Operator Terminal:** A simplified interface for machine operators.
