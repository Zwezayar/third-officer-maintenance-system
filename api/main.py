from fastapi import FastAPI
from datetime import datetime
import sqlite3
import logging
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from fastapi.responses import PlainTextResponse

logging.basicConfig(filename="/app/logs/api_audit.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

REQUESTS = Counter("api_requests_total", "Total API requests", ["endpoint"])
LATENCY = Histogram("api_request_latency_seconds", "API request latency", ["endpoint"])

def log_action(action, user, details):
    try:
        conn = sqlite3.connect("/app/database/ship_maintenance.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (action, user, timestamp, details)
            VALUES (?, ?, ?, ?)
        """, (action, user, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), details))
        conn.commit()
        conn.close()
        logging.info(f"Audit: {action} by {user}: {details}")
    except Exception as e:
        logging.error(f"Error logging action {action}: {str(e)}")

@app.get("/health")
async def health_check():
    with LATENCY.labels(endpoint="/health").time():
        log_action("health_check", "system", "Health check performed")
        return {"status": "healthy"}

@app.get("/alerts/overdue")
async def get_overdue_alerts():
    with LATENCY.labels(endpoint="/alerts/overdue").time():
        REQUESTS.labels(endpoint="/alerts/overdue").inc()
        try:
            conn = sqlite3.connect("/app/database/ship_maintenance.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, equipment, task, last_completed, next_due
                FROM maintenance_schedules
                WHERE next_due < ?
            """, (datetime.now().strftime("%Y-%m-%d"),))
            alerts = [
                {"id": row[0], "equipment": row[1], "task": row[2],
                 "last_completed": row[3], "next_due": row[4]}
                for row in cursor.fetchall()
            ]
            cursor.execute("""
                INSERT OR REPLACE INTO cache (key, value, timestamp)
                VALUES (?, ?, ?)
            """, ("alerts/overdue", str({"alerts": alerts}),
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            log_action("fetch_alerts", "system", f"Fetched {len(alerts)} overdue alerts")
            return {"alerts": alerts}
        except Exception as e:
            log_action("fetch_alerts_error", "system", f"Error fetching alerts: {str(e)}")
            raise

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    with LATENCY.labels(endpoint="/metrics").time():
        REQUESTS.labels(endpoint="/metrics").inc()
        log_action("fetch_metrics", "system", "Prometheus metrics fetched")
        return generate_latest(REGISTRY).decode("utf-8")
