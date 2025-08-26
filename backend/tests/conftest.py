# Test configuration and fixtures
import logging
from typing import Generator, Optional, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

# Import models and database setup
from database_models import Base
from database import get_db
from main import app
from const.config import config

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test database URL - use SQLite in memory for speed
TEST_DATABASE_URL = "sqlite:///:memory:"

def get_test_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
    Base.metadata.create_all(bind=engine)
    return engine

def get_test_db(engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create fresh tables for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_test_client(test_db: Session) -> TestClient:
    """Create test client with dependency override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        return test_client

def get_auth_headers(client: TestClient):
    """Get authentication headers for testing protected endpoints."""
    # Create a test user and get token
    test_user = {
        "email": "test@example.com",
        "password": "testpassword123",
        "re_password": "testpassword123",  # Add required confirmation password
        "first_name": "Test",
        "last_name": "User",
        "role": "EMPLOYEE"
    }
    
    # Register user using correct endpoint
    register_response = client.post("/auth/users/", json=test_user)
    
    # Login to get token using correct endpoint and format
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    
    login_response = client.post("/auth/token", json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # Return empty headers - tests will handle authentication errors appropriately
        return {}

# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_historical_machine_data(db: Session, machine_id: str = "test_machine",
                                     start_time: Optional[datetime] = None,
                                     duration_seconds: int = 3600,
                                     classification: str = "UPTIME",
                                     productivity: str = "productive"):
        """Create test historical machine data."""
        from database_models import HistoricalMachineData
        import uuid
        
        if start_time is None:
            start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        end_time = start_time + timedelta(seconds=duration_seconds)
        
        # Generate unique ID for historical machine data
        unique_id = str(uuid.uuid4())
        
        data = HistoricalMachineData(
            id=unique_id,  # Add the required id field
            machine_id=machine_id,
            name=config.MACHINE_ID_MAP.get(machine_id, "Test Machine"),
            start_timestamp=start_time,
            end_timestamp=end_time,
            duration_seconds=duration_seconds,
            classification=classification,
            productivity=productivity,
            utilisation_category=f"{productivity}_{classification.lower()}",
            shift="DAY",
            day_of_week="MONDAY",
            downtime_reason_name="Test Reason" if classification == "DOWNTIME" else None
        )
        
        db.add(data)
        db.commit()
        db.refresh(data)
        return data
    
    @staticmethod
    def create_cut_event(db: Session, machine_id: str = "test_machine",
                        timestamp: Optional[datetime] = None, cut_count: int = 1):
        """Create test cut event."""
        from database_models import CutEvent
        
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        event = CutEvent(
            machine_id=machine_id,
            timestamp_utc=timestamp,
            cut_count=cut_count
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    
    @staticmethod
    def create_maintenance_ticket(db: Session, machine_id: str = "test_machine",
                                status: str = "Open", priority: str = "Medium"):
        """Create test maintenance ticket."""
        from database_models import MaintenanceTicket
        
        ticket = MaintenanceTicket(
            description="Test maintenance issue description",
            machine_id=machine_id,
            status=status,
            priority=priority,
            incident_category="Mechanical",
            # Note: logged_time will use default value from model
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def create_production_run(db: Session, machine_id: str = "test_machine"):
        """Create test production run."""
        from database_models import ProductionRun, Product
        import hashlib
        
        # Create a unique product code based on machine_id to avoid constraint violations
        machine_hash = hashlib.md5(machine_id.encode()).hexdigest()[:6].upper()
        unique_product_code = f"TEST{machine_hash}"
        
        # Create a test product first
        product = Product(
            product_name=f"Test Product for {machine_id}",
            product_code=unique_product_code
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Create production run
        run = ProductionRun(
            machine_id=machine_id,
            product_id=product.id,
            start_time=datetime.now(timezone.utc) - timedelta(hours=2),
            end_time=datetime.now(timezone.utc),
            status="COMPLETED",
            scrap_length=5.5
        )
        
        db.add(run)
        db.commit()
        db.refresh(run)
        return run
    
    @staticmethod
    def create_comprehensive_test_data(db: Session, machine_id: str = "test_machine"):
        """Create a comprehensive set of test data for a machine."""
        base_time = datetime.now(timezone.utc) - timedelta(days=1)
        
        # Create various historical data points
        uptime_data = TestDataFactory.create_historical_machine_data(
            db, machine_id, base_time, 7200, "UPTIME", "productive"
        )
        
        downtime_data = TestDataFactory.create_historical_machine_data(
            db, machine_id, base_time + timedelta(hours=2), 1800, "DOWNTIME", "unproductive"
        )
        
        # Create cut events
        for i in range(10):
            TestDataFactory.create_cut_event(
                db, machine_id, base_time + timedelta(minutes=i*30), 5
            )
        
        # Create maintenance ticket
        ticket = TestDataFactory.create_maintenance_ticket(db, machine_id)
        
        # Create production run
        production_run = TestDataFactory.create_production_run(db, machine_id)
        
        return {
            "uptime_data": uptime_data,
            "downtime_data": downtime_data,
            "ticket": ticket,
            "production_run": production_run
        }

# Performance testing utilities
class PerformanceTimer:
    """Simple performance timer for testing endpoint speed."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
    
    @property
    def elapsed_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def elapsed_ms(self) -> float:
        return self.elapsed_seconds * 1000

# Test configuration
class TestConfig:
    """Test configuration constants."""
    
    # Performance thresholds (in milliseconds)
    FAST_ENDPOINT_THRESHOLD = 100    # Very fast endpoints
    MEDIUM_ENDPOINT_THRESHOLD = 500  # Medium complexity endpoints
    SLOW_ENDPOINT_THRESHOLD = 2000   # Complex analytics endpoints
    
    # Test data sizes
    SMALL_DATASET_SIZE = 100
    MEDIUM_DATASET_SIZE = 1000
    LARGE_DATASET_SIZE = 10000
    
    # Default test machine IDs
    TEST_MACHINE_IDS = ["test_machine_1", "test_machine_2", "test_machine_3"]
