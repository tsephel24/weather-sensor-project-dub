from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from . import models, schemas

def create_reading(db: Session, payload: schemas.MetricInput):
    try:
        ts = payload.timestamp or datetime.now(timezone.utc)

        for m_type, m_value in payload.metrics.items():
            db_obj = models.MetricReading(
                sensor_id=payload.sensor_id,
                metric_type=m_type,
                value=m_value,
                timestamp=ts
            )
            db.add(db_obj)

        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database commit failed")

def get_aggregated_stats(
        db: Session,
        sensor_ids: list[str] | None,
        metrics: list[str] | None,
        stat: schemas.Statistic,
        start: datetime | None,
        end: datetime | None
):
    if stat == schemas.Statistic.average:
        agg = func.avg(models.MetricReading.value)
    elif stat == schemas.Statistic.min:
        agg = func.min(models.MetricReading.value)
    elif stat == schemas.Statistic.max:
        agg = func.max(models.MetricReading.value)
    elif stat == schemas.Statistic.sum:
        agg = func.sum(models.MetricReading.value)

    query = db.query(
        models.MetricReading.sensor_id,
        models.MetricReading.metric_type,
        agg.label("result")
    )

    filters = []
    if sensor_ids:
        filters.append(models.MetricReading.sensor_id.in_(sensor_ids))
    if metrics:
        filters.append(models.MetricReading.metric_type.in_(metrics))

    if not start and not end:
        start = datetime.now(timezone.utc) - timedelta(days=1)

    if start:
        filters.append(models.MetricReading.timestamp >= start)
    if end:
        filters.append(models.MetricReading.timestamp <= end)

    query = query.filter(and_(*filters))
    query = query.group_by(models.MetricReading.sensor_id, models.MetricReading.metric_type)

    return [
        {
            "sensor_id": row.sensor_id,
            "metric": row.metric_type,
            "statistic": stat.value,
            "value": row.result
        }
        for row in query.all()
    ]