from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from .database import Base

class MetricReading(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, index=True)
    metric_type = Column(String, index=True)
    value = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)