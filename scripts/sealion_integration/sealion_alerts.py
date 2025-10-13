import requests
import json
import sqlite3
from datetime import datetime

def get_db():
    conn = sqlite3.connect("database/ship_maintenance.db")
    conn.row_factory = sqlite3.Row
    return conn

def check_maintenance_alerts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maintenance_schedules WHERE next_due <= ?", (datetime.now().strftime("%Y-%m-%d"),))
    overdue = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    alerts = []
    for item in overdue:
        alerts.append({
            "equipment": item["equipment"],
            "task": item["task"],
            "due_date": item["next_due"],
            "regulation": item["regulation"],
            "alert": f"Overdue: {item['task']} for {item['equipment']} due by {item['next_due']}"
        })
    
    # Mock SEA-LION API call
    mock_sealion_url = "http://localhost:8080/sealion/alerts"
    try:
        response = requests.post(mock_sealion_url, json=alerts)
        print(f"SEA-LION Alerts sent: {response.status_code}")
    except requests.ConnectionError:
        print("Mock SEA-LION API not available - storing locally")
        with open("logs/sealion_alerts.json", "w") as f:
            json.dump(alerts, f, indent=2)
    
    return alerts

if __name__ == "__main__":
    alerts = check_maintenance_alerts()
    print(json.dumps(alerts, indent=2))

