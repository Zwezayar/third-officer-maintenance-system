import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect("maintenance.db")
cursor = conn.cursor()

# Create schedules table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment TEXT NOT NULL,
        task TEXT NOT NULL,
        start_date TEXT NOT NULL,
        due_date TEXT NOT NULL
    )
""")

# Seed initial data
schedules = [
    ("Lifeboat 1", "Inspection", "2025-09-01", "2025-10-21"),
    ("Fire Extinguisher A", "Pressure Test", "2025-08-15", "2025-10-20"),
    ("Engine Room Pump", "Lubrication", "2025-10-01", "2025-10-22")
]
cursor.executemany("INSERT OR IGNORE INTO schedules (equipment, task, start_date, due_date) VALUES (?, ?, ?, ?)", schedules)
conn.commit()
conn.close()
print("Created maintenance.db with schedules table")
