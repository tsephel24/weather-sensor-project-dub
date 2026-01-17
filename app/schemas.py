from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

class Statistic(str, Enum):
    min = "min"
    max = "max"
    sum = "sum"
    average = "average"

class MetricInput(BaseModel):
    sensor_id: str = Field(..., min_length=1, description="Unique ID of the sensor")
    metrics: Dict[str, float] = Field(..., description="Key-value pairs of metrics")
    timestamp: Optional[datetime] = None

class MetricResponse(BaseModel):
    sensor_id: str
    metric: str
    statistic: str
    value: Optional[float]

    model_config = ConfigDict(from_attributes=True)