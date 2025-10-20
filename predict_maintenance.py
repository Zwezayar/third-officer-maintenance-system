import pandas as pd
import sqlite3
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import pickle
import os

os.makedirs("/app/models", exist_ok=True)
conn = sqlite3.connect("/app/database/ship_maintenance.db")
df = pd.read_sql_query("SELECT * FROM maintenance_schedules", conn)
conn.close()

le = LabelEncoder()
df["equipment_encoded"] = le.fit_transform(df["equipment"])
df["days_until_due"] = (pd.to_datetime(df["next_due"]) - pd.to_datetime("2025-10-20")).dt.days
X = df[["equipment_encoded", "days_until_due"]]
y = (df["days_until_due"] < 30).astype(int)  # Predict if due soon

if len(set(y)) < 2:
    print("Warning: Only one class in target variable. Using dummy model.")
    with open("/app/models/predictor.pkl", "wb") as f:
        pickle.dump({"predict_proba": lambda X: [[0.5, 0.5] for _ in range(len(X))]}, f)
else:
    model = LogisticRegression()
    model.fit(X, y)
    with open("/app/models/predictor.pkl", "wb") as f:
        pickle.dump(model, f)
with open("/app/models/encoder.pkl", "wb") as f:
    pickle.dump(le, f)
