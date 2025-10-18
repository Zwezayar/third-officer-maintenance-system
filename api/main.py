from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest
import sqlite3
from datetime import datetime
import logging

app = FastAPI()

# Setup logging
logging.basicConfig(
    filename="logs/api_audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Prometheus metrics
REQUESTS = Counter("api_requests_total", "Total API requests", ["endpoint"])
REQUEST_LATENCY = Histogram("api_request_latency_seconds", "API request latency", ["endpoint"])

# Database connection
def get_db():
    conn = sqlite3.connect("database/ship_maintenance.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health")
async def health():
    REQUESTS.labels(endpoint="/health").inc()
    with REQUEST_LATENCY.labels(endpoint="/health").time():
        logging.info("Health check accessed")
        return {"status": "healthy"}

@app.get("/alerts/overdue")
async def overdue_alerts():
    REQUESTS.labels(endpoint="/alerts/overdue").inc()
    with REQUEST_LATENCY.labels(endpoint="/alerts/overdue").time():
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM maintenance_schedules 
                WHERE next_due < ?
            """, (datetime.now().strftime("%Y-%m-%d"),))
            alerts = [dict(row) for row in cursor.fetchall()]
            conn.close()
            logging.info("Overdue alerts retrieved")
            return {"alerts": alerts}
        except Exception as e:
            logging.error(f"Failed to retrieve overdue alerts: {str(e)}")
            return {"error": str(e)}

@app.get("/metrics")
async def metrics():
    logging.info("Metrics endpoint accessed")
    return generate_latest()
