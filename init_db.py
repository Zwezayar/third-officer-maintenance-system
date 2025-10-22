import sqlite3
from datetime import datetime

conn = sqlite3.connect('/app/database/maintenance.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance_schedule (
        id INTEGER PRIMARY KEY,
        equipment TEXT NOT NULL,
        task TEXT NOT NULL,
        start_date TEXT NOT NULL,
        due_date TEXT NOT NULL
    )
''')

cursor.executemany('''
    INSERT INTO maintenance_schedule (id, equipment, task, start_date, due_date)
    VALUES (?, ?, ?, ?, ?)
''', [
    (1, 'Lifeboat 1', 'Inspection', '2025-09-01', '2025-10-21'),
    (2, 'Fire Extinguisher A', 'Pressure Test', '2025-08-15', '2025-10-20'),
    (3, 'Engine Room Pump', 'Lubrication', '2025-10-01', '2025-10-22')
])

conn.commit()
conn.close()
print("Database initialized successfully.")
