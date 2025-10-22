from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
import sqlite3
from datetime import datetime

app = FastAPI()

api_requests = Counter('api_requests_total', 'Total API requests', ['endpoint'])

def get_db_connection():
    conn = sqlite3.connect('/app/database/maintenance.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/metrics")
async def metrics():
    api_requests.labels(endpoint="/metrics").inc()
    return generate_latest()

@app.get("/maintenance")
async def maintenance():
    api_requests.labels(endpoint="/maintenance").inc()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maintenance_schedule")
    schedules = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"schedules": [[s['id'], s['equipment'], s['task'], s['start_date'], s['due_date']] for s in schedules]}
