from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
from fastapi.responses import PlainTextResponse
import sqlite3
from contextlib import asynccontextmanager

# Prometheus metrics
REQUESTS = Counter('api_requests_total', 'Total API requests', ['endpoint'])

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
