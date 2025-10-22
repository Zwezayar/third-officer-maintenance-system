from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
import sqlite3

app = FastAPI()
metrics_requests = Counter("api_requests_total", "Total API requests", ["endpoint"])

@app.get("/metrics")
async def metrics():
    metrics_requests.labels(endpoint="/metrics").inc()
    return generate_latest()

@app.get("/maintenance")
async def get_maintenance():
    metrics_requests.labels(endpoint="/maintenance").inc()
    conn = sqlite3.connect("/app/database/ship_maintenance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maintenance_schedules")
    schedules = cursor.fetchall()
    conn.close()
    return {"schedules": schedules}
