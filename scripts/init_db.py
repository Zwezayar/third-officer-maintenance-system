import sqlite3
import os

def init_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect("database/ship_maintenance.db")
    cursor = conn.cursor()

    # Predictions table (from Task 3)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY,
            equipment TEXT,
            risk_level TEXT,
            issue TEXT,
            mitigation TEXT,
            regulation TEXT
        )
    """)

    # Training records (from Task 4)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER,
            crew_id TEXT,
            title TEXT,
            completed_at TEXT,
            regulation TEXT
        )
    """)

    # Maintenance schedules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment TEXT,
            task TEXT,
            frequency TEXT,
            regulation TEXT,
            last_completed TEXT,
            next_due TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized: database/ship_maintenance.db")

if __name__ == "__main__":
    init_db()
