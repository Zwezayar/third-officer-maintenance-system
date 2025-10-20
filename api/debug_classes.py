import pandas as pd
import sqlite3

conn = sqlite3.connect("/app/database/ship_maintenance.db")
df = pd.read_sql_query("SELECT * FROM maintenance_schedules", conn)
conn.close()

df["days_until_due"] = (pd.to_datetime(df["next_due"]) - pd.to_datetime("2025-10-20")).dt.days
y = (df["days_until_due"] < 30).astype(int)
print("Classes in y:", list(y))
print("DataFrame:\n", df[["equipment", "next_due", "days_until_due"]])
