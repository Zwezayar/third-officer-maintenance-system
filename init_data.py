import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("/app/database/ship_maintenance.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_schedules (
        id INTEGER PRIMARY KEY,
        equipment TEXT,
        task TEXT,
        last_completed TEXT,
        next_due TEXT
    )
""")
cursor.execute("DELETE FROM maintenance_schedules")  # Clear existing data
sample_data = [
    ("Lifeboat 1", "Inspection", "2025-09-01", "2025-10-21"),
    ("Fire Extinguisher A", "Pressure Test", "2025-08-15", "2025-10-20"),
    ("Engine Room Pump", "Lubrication", "2025-10-01", "2025-10-22")
]
cursor.executemany("INSERT INTO maintenance_schedules (equipment, task, last_completed, next_due) VALUES (?, ?, ?, ?)", sample_data)
conn.commit()
conn.close()
