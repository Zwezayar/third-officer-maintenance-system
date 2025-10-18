from fastapi import FastAPI
import sqlite3
from datetime import datetime
from prometheus_client import Counter, Histogram, generate_latest
import logging

# Configure logging
logging.basicConfig(filename="/app/logs/api_audit.log", level=logging.INFO)

app = FastAPI()

# Prometheus metrics
REQUESTS = Counter('api_requests_total', 'Total API requests', ['endpoint'])
LATENCY = Histogram('api_request_latency_seconds', 'API request latency', ['endpoint'])

@app.get("/health")
async def health_check():
    with LATENCY.labels(endpoint='/health').time():
        REQUESTS.labels(endpoint='/health').inc()
        return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    with LATENCY.labels(endpoint='/metrics').time():
        REQUESTS.labels(endpoint='/metrics').inc()
        return generate_latest()

@app.get("/alerts/overdue")
async def get_overdue_alerts():
    with LATENCY.labels(endpoint='/alerts/overdue').time():
        REQUESTS.labels(endpoint='/alerts/overdue').inc()
        try:
            conn = sqlite3.connect("/app/database/ship_maintenance.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM maintenance_schedules
                WHERE next_due < ?
            """, (datetime.now().strftime("%Y-%m-%d"),))
            alerts = [
                {"id": row[0], "equipment": row[1], "task": row[2], "last_completed": row[3], "next_due": row[4]}
                for row in cursor.fetchall()
            ]
            # Cache the response
            cursor.execute("""
                INSERT OR REPLACE INTO cache (key, value, timestamp)
                VALUES (?, ?, ?)
            """, ("alerts/overdue", str({"alerts": alerts}), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            logging.info(f"Cached /alerts/overdue response: {alerts}")
            return {"alerts": alerts}
        except Exception as e:
            logging.error(f"Error fetching overdue alerts: {str(e)}")
            raise
