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
y = (df["days_until_due"] < 30).astype(int)

if len(set(y)) < 2:
    print("Warning: Only one class in target variable. Creating default probabilities.")
    df["failure_risk"] = [0.9 if days < 30 else 0.1 for days in df["days_until_due"]]
    with open("/app/models/predictor.pkl", "wb") as f:
        pickle.dump({"predict_proba": lambda X: [[1 - p, p] for p in df["failure_risk"]]}, f)
else:
    model = LogisticRegression()
    model.fit(X, y)
    with open("/app/models/predictor.pkl", "wb") as f:
        pickle.dump(model, f)
with open("/app/models/encoder.pkl", "wb") as f:
    pickle.dump(le, f)
