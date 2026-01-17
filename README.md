# Weather Sensor Service (PoC)

## Overview
A RESTful API built with **FastAPI** and **Python 3.13** to ingest weather metrics and provide statistical aggregations (Min, Max, Sum, Average).

## Design Strategy

### Database Choice: SQLite 
For this Proof of Concept, I utilized **SQLite** (via SQLAlchemy) to ensure the application is portable and can be run immediately without complex environment setup.

However, for a production environment handling high-velocity sensor data, I would migrate to **AWS DynamoDB** or a similar time-series capable solution to handle scale.
## Setup & Execution

### Prerequisites
* Python 3.13+
* Pipenv (Install via `pip install pipenv`)

### 1. Installation
Initialize the virtual environment and install dependencies:
```bash
pipenv install --dev
```

### 2. Running the Server
Start the service:
```bash
pipenv run uvicorn app.main:app
```
The interactive API documentation will be available at: **http://127.0.0.1:8000/docs**

*(For development with hot-reload, use: `pipenv run uvicorn app.main:app --reload`)*

### 3. Running Tests
Run the integration test suite:
```bash
pipenv run python -m pytest
```

## Quick Start (Manual Test)

**1. Ingest Data (POST)**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/metrics' \
  -H 'Content-Type: application/json' \
  -d '{ "sensor_id": "sensor_1", "metrics": { "temperature": 23.5, "humidity": 45.0 } }'
```

**2. Query Data (GET)**
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/stats?sensor=sensor_1&metric=temperature&statistic=average'
```
