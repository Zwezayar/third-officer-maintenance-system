from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest
import sqlite3

app = FastAPI()
metrics_requests = Counter("api_requests_total", "Total API requests", ["endpoint"])

@app.get("/metrics")
async def metrics():
    metrics_requests.labels(endpoint="/metrics").inc()
    return Response(content=generate_latest(), media_type="text/plain; version=0.0.4; charset=utf-8")

@app.get("/maintenance")
async def get_maintenance():
    metrics_requests.labels(endpoint="/maintenance").inc()
    conn = sqlite3.connect("/app/database/ship_maintenance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maintenance_schedules")
    schedules = cursor.fetchall()
    conn.close()
    return {"schedules": schedules}
