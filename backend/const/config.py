from typing import Dict
from datetime import time
import os


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



class Config:
    ROOT_DIR: str = ROOT_DIR

    # ===== API CONFIGURATION =====
    BASE_URL: str = 'https://css-limited.fourjaw.app/rest/api/v0.1'

    API_KEY: str= os.getenv('FOURJAW_API_KEY')

    SECURE_HEADER: Dict[str, str] = {
        'X-API-KEY': API_KEY
    }

    # ===== DATA PROCESSOR CONFIGURATION =====
    DAY_SHIFT_START = time(6, 0)
    DAY_SHIFT_END = time(18, 0)

    # Define how FourJaw statuses map to our utilisation categories
    FOURJAW_STATUS_MAP = {
        "production": "Productive Uptime",
        "changeover": "Productive Downtime",
        "setting": "Productive Downtime",
        "idle": "Unproductive Downtime",
        "maintenance": "Unproductive Downtime",
        "breakdown": "Unproductive Downtime"
    }

    FOURJAW_POLLING_INTERVAL_SECONDS = 5
    FOURJAW_HISTORICAL_FETCH_DAYS = 30


    # ===== MACHINE IDENTIFICATION =====
    MACHINE_IDS = [
        '6809f67ffc54c40ff1b489cf', 
        '6809f8df20e024b627b489eb', 
        '6809f8df20e024b627b489ed', 
        '6809f8df20e024b627b489f0', 
        '6809f8df20e024b627b489f2'
    ]
    MACHINE_ID_MAP = {
        '6809f67ffc54c40ff1b489cf': 'Mill 1',
        '6809f8df20e024b627b489eb': 'Mill 2',
        '6809f8df20e024b627b489ed': 'Mill 3',
        '6809f8df20e024b627b489f0': 'Spot 1 (TBC)', 
        '6809f8df20e024b627b489f2': 'Spot 2 (TBC)'
    }


    # ===== FastAPI CONFIGURATION =====
    # --- CORS Middleware ---
    # This allows your React frontend (running on a different port) to communicate with this backend.
    # In production, you should restrict the origins to your actual frontend domain.
    ORIGINS = [
        "http://localhost",
        "http://localhost:5173",  # Default Vite dev server port
        "http://localhost:3000",  # Default Create React App port
    ]

    # --- SECURITY CONFIGURATION ---
    # In production, generate a random key with: openssl rand -hex 32
    SECRET_KEY = os.getenv('SECRET_KEY', 'my-super-secret-key')
    ALGORITHM = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = 60


    # ===== MQTT CONFIGURATION =====
    MQTT_BROKER_HOST = "mosquitto" # The service name from docker-compose
    MQTT_BROKER_PORT = 1883
    MQTT_TOPIC = "plc/events/cuts"
    # MQTT_USER = "your_username" # Uncomment if needed
    # MQTT_PASSWORD = "your_password" # Uncomment if needed
        