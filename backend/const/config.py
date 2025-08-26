from typing import Dict, List, Optional
from datetime import time
import os
import json
from pathlib import Path

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigurationError(Exception):
    """Raised when there's an error in configuration."""
    pass

class Config:
    """
    Centralized configuration management using environment variables.
    All hardcoded values moved to environment variables with sensible defaults.
    """
    ROOT_DIR: str = ROOT_DIR

    def __init__(self):
        """Initialize and validate configuration."""
        # Validate required environment variables
        self._api_key = os.getenv('FOURJAW_API_KEY')
        if not self._api_key:
            raise ConfigurationError("FOURJAW_API_KEY environment variable is required")
        
        self._secret_key = os.getenv('SECRET_KEY')
        if not self._secret_key:
            raise ConfigurationError("SECRET_KEY environment variable is required")

    # ===== API CONFIGURATION =====
    BASE_URL: str = os.getenv('FOURJAW_BASE_URL', 'https://css-limited.fourjaw.app/rest/api/v0.1')
    
    @property
    def API_KEY(self) -> str:
        assert self._api_key is not None, "API_KEY should be validated in __init__"
        return self._api_key

    @property
    def SECURE_HEADER(self) -> Dict[str, str]:
        return {'X-API-KEY': self.API_KEY}

    # ===== DATA PROCESSOR CONFIGURATION =====
    @classmethod
    def _parse_time(cls, time_str: str, default: time) -> time:
        """Parse time string in HH:MM format."""
        try:
            hour, minute = map(int, time_str.split(':'))
            return time(hour, minute)
        except (ValueError, AttributeError):
            return default

    @property
    def DAY_SHIFT_START(self) -> time:
        return self._parse_time(os.getenv('DAY_SHIFT_START', '06:00'), time(6, 0))
    
    @property
    def DAY_SHIFT_END(self) -> time:
        return self._parse_time(os.getenv('DAY_SHIFT_END', '18:00'), time(18, 0))

    # Define how FourJaw statuses map to our utilisation categories
    @property
    def FOURJAW_STATUS_MAP(self) -> Dict[str, str]:
        """Load status mapping from environment or use defaults."""
        default_map = {
            "production": "Productive Uptime",
            "changeover": "Productive Downtime", 
            "setting": "Productive Downtime",
            "idle": "Unproductive Downtime",
            "maintenance": "Unproductive Downtime",
            "breakdown": "Unproductive Downtime"
        }
        
        map_str = os.getenv('FOURJAW_STATUS_MAP')
        if map_str:
            try:
                return json.loads(map_str)
            except json.JSONDecodeError:
                print(f"Warning: Invalid FOURJAW_STATUS_MAP format, using defaults")
                return default_map
        return default_map

    FOURJAW_POLLING_INTERVAL_SECONDS: int = int(os.getenv('FOURJAW_POLLING_INTERVAL_SECONDS', '5'))
    FOURJAW_HISTORICAL_FETCH_DAYS: int = int(os.getenv('FOURJAW_HISTORICAL_FETCH_DAYS', '30'))

    # ===== MACHINE IDENTIFICATION =====
    @property
    def MACHINE_IDS(self) -> List[str]:
        """Load machine IDs from environment variable."""
        ids_str = os.getenv('MACHINE_IDS')
        if ids_str:
            try:
                return json.loads(ids_str)
            except json.JSONDecodeError:
                print(f"Warning: Invalid MACHINE_IDS format, using defaults")
        
        # Default machine IDs
        return [
            '6809f67ffc54c40ff1b489cf', 
            '6809f8df20e024b627b489eb', 
            '6809f8df20e024b627b489ed', 
            '6809f8df20e024b627b489f0', 
            '6809f8df20e024b627b489f2'
        ]
    
    @property
    def MACHINE_ID_MAP(self) -> Dict[str, str]:
        """Load machine ID to name mapping from environment variable."""
        map_str = os.getenv('MACHINE_ID_MAP')
        if map_str:
            try:
                return json.loads(map_str)
            except json.JSONDecodeError:
                print(f"Warning: Invalid MACHINE_ID_MAP format, using defaults")
        
        # Default mapping
        return {
            '6809f67ffc54c40ff1b489cf': 'Mill 1',
            '6809f8df20e024b627b489eb': 'Mill 2',
            '6809f8df20e024b627b489ed': 'Mill 3',
            '6809f8df20e024b627b489f0': 'Spot 1 (TBC)', 
            '6809f8df20e024b627b489f2': 'Spot 2 (TBC)'
        }

    # ===== FastAPI CONFIGURATION =====
    @property
    def ORIGINS(self) -> List[str]:
        """Load CORS origins from environment variable."""
        origins_str = os.getenv('CORS_ORIGINS')
        if origins_str:
            try:
                return json.loads(origins_str)
            except json.JSONDecodeError:
                # Try comma-separated format
                return [origin.strip() for origin in origins_str.split(',')]
        
        # Default origins for development
        return [
            "http://localhost",
            "http://localhost:5173",  # Default Vite dev server port
            "http://localhost:3000",  # Default Create React App port
        ]

    # ===== SECURITY CONFIGURATION =====
    @property
    def SECRET_KEY(self) -> str:
        assert self._secret_key is not None, "SECRET_KEY should be validated in __init__"
        return self._secret_key
    
    ALGORITHM: str = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES', str(60 * 24 * 7)))

    # ===== MQTT CONFIGURATION =====
    MQTT_BROKER_HOST: str = os.getenv('MQTT_BROKER_HOST', 'mosquitto')
    MQTT_BROKER_PORT: int = int(os.getenv('MQTT_BROKER_PORT', '1883'))
    MQTT_TOPIC: str = os.getenv('MQTT_TOPIC', 'plc/events/cuts')
    MQTT_USER: Optional[str] = os.getenv('MQTT_USER')
    MQTT_PASSWORD: Optional[str] = os.getenv('MQTT_PASSWORD')

    # ===== BACKGROUND TASK CONFIGURATION =====
    BACKGROUND_TASK_INTERVAL_SECONDS: int = int(os.getenv('BACKGROUND_TASK_INTERVAL_SECONDS', '300'))  # 5 minutes
    ENABLE_BACKGROUND_TASKS: bool = os.getenv('ENABLE_BACKGROUND_TASKS', 'true').lower() == 'true'

    def validate_config(self) -> None:
        """Validate critical configuration values."""
        print(f"[INFO] Configuration loaded successfully")
        print(f"[INFO] Machine IDs: {len(self.MACHINE_IDS)} configured")
        print(f"[INFO] CORS Origins: {len(self.ORIGINS)} configured")

# Create global configuration instance
try:
    config = Config()
    config.validate_config()
except ConfigurationError as e:
    print(f"[ERROR] Configuration Error: {e}")
    raise
        
