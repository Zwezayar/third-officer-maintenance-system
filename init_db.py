import sqlite3

conn = sqlite3.connect("maritime_db.db")
cursor = conn.cursor()

# Drop existing tables to clean duplicates
cursor.execute("DROP TABLE IF EXISTS maintenance_tasks")
cursor.execute("DROP TABLE IF EXISTS equipment")
cursor.execute("DROP TABLE IF EXISTS tasks")
cursor.execute("DROP TABLE IF EXISTS drill_training")
cursor.execute("DROP TABLE IF EXISTS lsa_ffa_inventory")

# Maintenance Tasks Table
cursor.execute("""
    CREATE TABLE maintenance_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment TEXT NOT NULL,
        task TEXT NOT NULL,
        due_date TEXT NOT NULL,
        status TEXT NOT NULL,
        officer_id TEXT NOT NULL
    )
""")

# Equipment Table
cursor.execute("""
    CREATE TABLE equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
""")

# Tasks Table
cursor.execute("""
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
""")

# Drill and Training Table
cursor.execute("""
    CREATE TABLE drill_training (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        location TEXT NOT NULL,
        type_of_drill TEXT NOT NULL,
        duration TEXT NOT NULL,
        attendances TEXT NOT NULL,
        storage_url TEXT,
        scenario_file_path TEXT
    )
""")

# LSA & FFA Inventory Table
cursor.execute("""
    CREATE TABLE lsa_ffa_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL,
        description TEXT,
        units INTEGER NOT NULL,
        order_date TEXT,
        remark TEXT
    )
""")

# Insert default equipment
cursor.execute("INSERT OR IGNORE INTO equipment (name) VALUES (?)", ("Lifeboat1",))
cursor.execute("INSERT OR IGNORE INTO equipment (name) VALUES (?)", ("Lifeboat2",))
cursor.execute("INSERT OR IGNORE INTO equipment (name) VALUES (?)", ("Fire Extinguisher",))
cursor.execute("INSERT OR IGNORE INTO equipment (name) VALUES (?)", ("SCBA 01",))
cursor.execute("INSERT OR IGNORE INTO equipment (name) VALUES (?)", ("EEBD",))

# Insert default tasks
cursor.execute("INSERT OR IGNORE INTO tasks (name) VALUES (?)", ("Inspection",))
cursor.execute("INSERT OR IGNORE INTO tasks (name) VALUES (?)", ("Maintenance",))
cursor.execute("INSERT OR IGNORE INTO tasks (name) VALUES (?)", ("Testing",))
cursor.execute("INSERT OR IGNORE INTO tasks (name) VALUES (?)", ("Repair",))
cursor.execute("INSERT OR IGNORE INTO tasks (name) VALUES (?)", ("Check Air Pressure",))

# Insert sample maintenance tasks
cursor.execute("INSERT OR IGNORE INTO maintenance_tasks (equipment, task, due_date, status, officer_id) VALUES (?, ?, ?, ?, ?)", 
              ("SCBA 01", "Check Air Pressure", "2025-10-24", "Pending", "ZWE123"))
cursor.execute("INSERT OR IGNORE INTO maintenance_tasks (equipment, task, due_date, status, officer_id) VALUES (?, ?, ?, ?, ?)", 
              ("Lifeboat2", "Inspection", "2025-10-10", "Pending", "ZWE123"))
cursor.execute("INSERT OR IGNORE INTO maintenance_tasks (equipment, task, due_date, status, officer_id) VALUES (?, ?, ?, ?, ?)", 
              ("EEBD", "Inspection", "2025-10-25", "Pending", "04"))

# Insert sample drill and training
cursor.execute("INSERT OR IGNORE INTO drill_training (date, time, location, type_of_drill, duration, attendances, storage_url, scenario_file_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
              ("2025-10-25", "10:00", "Bridge Deck", "Fire Drill", "1h", "ZWE123,CREW456", "http://example.com/drill1", "/files/fire_drill.pdf"))

# Insert sample LSA & FFA inventory
cursor.execute("INSERT OR IGNORE INTO lsa_ffa_inventory (name, code, description, units, order_date, remark) VALUES (?, ?, ?, ?, ?, ?)", 
              ("Lifejacket", "LJ001", "Standard lifejacket", 50, "2025-10-01", "Ordered for next voyage"))

conn.commit()
conn.close()
print("Database initialized with equipment, tasks, maintenance tasks, drill and training, and LSA & FFA inventory.")
