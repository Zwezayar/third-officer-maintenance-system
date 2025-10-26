from fastapi import FastAPI, Response
from prometheus_client import Counter, generate_latest, REGISTRY
import sqlite3
from datetime import datetime

app = FastAPI()

api_requests = Counter('api_requests_total', 'Total API requests', ['endpoint'])

def get_db_connection():
    conn = sqlite3.connect('/app/database/maintenance.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
async def root():
    api_requests.labels(endpoint="/").inc()
    return {"message": "Welcome to the Third Officer Maintenance System API"}

@app.get("/metrics")
async def metrics():
    api_requests.labels(endpoint="/metrics").inc()
    return Response(content=generate_latest(REGISTRY), media_type="text/plain; version=0.0.4; charset=utf-8")

@app.get("/maintenance")
async def maintenance():
    api_requests.labels(endpoint="/maintenance").inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maintenance_schedule")
    schedules = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"schedules": [[s['id'], s['equipment'], s['task'], s['start_date'], s['due_date']] for s in schedules]}
