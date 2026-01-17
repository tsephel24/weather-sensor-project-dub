from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)

def test_ingest_metrics_happy_path():
    """Test inserting metrics works correctly."""
    response = client.post("/metrics", json={
        "sensor_id": "sensor_1",
        "metrics": {"temperature": 25.5, "humidity": 60.0}
    })
    assert response.status_code == 201
    assert response.json() == {"status": "success"}

def test_calculate_average_logic():
    """Test that the average calculation is accurate."""
    sensor = "sensor_calc_test"
    client.post("/metrics", json={"sensor_id": sensor, "metrics": {"temp": 10.0}})
    client.post("/metrics", json={"sensor_id": sensor, "metrics": {"temp": 20.0}})
    client.post("/metrics", json={"sensor_id": sensor, "metrics": {"temp": 30.0}})

    response = client.get(f"/stats?sensor={sensor}&metric=temp&statistic=average")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["value"] == 20.0

def test_date_range_validation():
    """Test that asking for > 1 month returns 400 Error."""
    response = client.get(
        "/stats?metric=temp&start_date=2023-01-01T00:00:00&end_date=2023-03-01T00:00:00"
    )
    assert response.status_code == 400
    assert "Date range cannot exceed 1 month" in response.json()["detail"]