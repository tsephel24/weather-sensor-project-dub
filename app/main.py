from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from . import database, models, schemas, crud

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Weather Sensor Service")

@app.post("/metrics", status_code=201)
def ingest_metrics(payload: schemas.MetricInput, db: Session = Depends(database.get_db)):
    """Ingests new sensor readings (temperature, humidity, etc)."""
    crud.create_reading(db, payload)
    return {"status": "success"}

@app.get("/stats", response_model=List[schemas.MetricResponse])
def query_stats(
        sensor_ids: Optional[List[str]] = Query(None, alias="sensor"),
        metrics: Optional[List[str]] = Query(None, alias="metric"),
        statistic: schemas.Statistic = schemas.Statistic.average,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(database.get_db)
):
    """Calculates aggregated stats. Defaults to last 24h if no dates provided."""
    if start_date and end_date and (end_date - start_date).days > 31:
        raise HTTPException(status_code=400, detail="Date range cannot exceed 1 month")

    return crud.get_aggregated_stats(db, sensor_ids, metrics, statistic, start_date, end_date)