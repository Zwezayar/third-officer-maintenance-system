import sqlite3
import json

def migrate_predictions():
    """Migrate Task 3 predictions from JSON to SQLite database."""
    try:
        with open("docs/task3_final_predictions.json", "r") as f:
            predictions = json.load(f)
    except FileNotFoundError:
        print("Error: docs/task3_final_predictions.json not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    conn = sqlite3.connect("database/ship_maintenance.db")
    cursor = conn.cursor()

    for pred in predictions:
        cursor.execute("""
            INSERT INTO predictions (equipment, risk_level, issue, mitigation, regulation)
            VALUES (?, ?, ?, ?, ?)
        """, (
            pred.get("item", ""),       # equipment
            pred.get("risk", ""),       # risk_level
            pred.get("note", ""),       # issue
            "",                         # mitigation (empty)
            ""                          # regulation (empty)
        ))

    conn.commit()
    conn.close()
    print("Predictions migrated to database successfully")

if __name__ == "__main__":
    migrate_predictions()
