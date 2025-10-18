from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import sqlite3
from datetime import datetime
from prometheus_client import Counter, Histogram, generate_latest
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Prometheus metrics
api_requests_total = Counter('api_requests_total', 'Total API requests', ['endpoint'])
api_request_latency_seconds = Histogram('api_request_latency_seconds', 'API request latency', ['endpoint'])

def get_db():
    conn = sqlite3.connect("/app/database/ship_maintenance.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health")
async def health_check():
    start_time = time.time()
    api_requests_total.labels(endpoint="/health").inc()
    latency = time.time() - start_time
    api_request_latency_seconds.labels(endpoint="/health").observe(latency)
    return {"status": "healthy"}

@app.get("/alerts/overdue")
async def get_overdue_alerts():
    start_time = time.time()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM maintenance_schedules 
        WHERE next_due < ?
    """, (datetime.now().strftime("%Y-%m-%d"),))
    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    api_requests_total.labels(endpoint="/alerts/overdue").inc()
    latency = time.time() - start_time
    api_request_latency_seconds.labels(endpoint="/alerts/overdue").observe(latency)
    return {"alerts": alerts}

@app.get("/debug")
async def debug():
    return {"message": "Debug endpoint", "metrics_mounted": True}

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return generate_latest()

# Debug middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response
