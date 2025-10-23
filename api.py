from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, generate_latest
from fastapi.responses import PlainTextResponse
import sqlite3
from contextlib import asynccontextmanager
from pydantic import BaseModel
from datetime import datetime

# Prometheus metrics
REQUESTS = Counter('api_requests_total', 'Total API requests', ['endpoint'])

# Pydantic model for schedule input
class ScheduleCreate(BaseModel):
    equipment: str
    task: str
    start_date: str
    due_date: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/metrics")
async def metrics():
    REQUESTS.labels(endpoint="/metrics").inc()
    return PlainTextResponse(generate_latest())

@app.get("/maintenance")
async def maintenance():
    REQUESTS.labels(endpoint="/maintenance").inc()
    conn = sqlite3.connect("maintenance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedules")
    schedules = cursor.fetchall()
    conn.close()
    return {"schedules": schedules}

@app.post("/maintenance")
async def create_maintenance(schedule: ScheduleCreate):
    REQUESTS.labels(endpoint="/maintenance").inc()
    try:
        # Validate dates
        datetime.strptime(schedule.start_date, "%Y-%m-%d")
        datetime.strptime(schedule.due_date, "%Y-%m-%d")
        conn = sqlite3.connect("maintenance.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO schedules (equipment, task, start_date, due_date) VALUES (?, ?, ?, ?)",
            (schedule.equipment, schedule.task, schedule.start_date, schedule.due_date)
        )
        conn.commit()
        schedule_id = cursor.lastrowid
        conn.close()
        return {"id": schedule_id, "message": "Schedule created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating schedule: {e}")
