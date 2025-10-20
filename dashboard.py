import streamlit as st
import pandas as pd
import sqlite3
import pickle
import requests
from datetime import datetime

st.title("Third Officer Maintenance Dashboard")

# Overdue Maintenance Alerts
st.header("Overdue Maintenance Alerts")
conn = sqlite3.connect("/app/database/ship_maintenance.db")
df = pd.read_sql_query("SELECT * FROM maintenance_schedules WHERE next_due <= ?", conn, params=(datetime.now().strftime('%Y-%m-%d'),))
conn.close()
st.table(df)

# API Request Metrics
st.header("API Request Metrics")
response = requests.get("http://api:8000/metrics")
metrics = []
for line in response.text.splitlines():
    if line.startswith("api_requests_total"):
        endpoint = line.split('{endpoint="')[1].split('"}')[0]
        value = float(line.split(' ')[-1])
        metrics.append({"metric": endpoint, "value": value})
st.table(pd.DataFrame(metrics))

# API Requests Over Time
st.header("API Requests Over Time")
try:
    response = requests.get("http://prometheus:9090/api/v1/query_range?query=api_requests_total&start=2025-10-20T00:00:00Z&end=2025-10-20T23:59:59Z&step=300s")
    data = response.json()["data"]["result"]
    if data:
        df = pd.DataFrame(data[0]["values"], columns=["timestamp", "value"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df["value"] = df["value"].astype(float)
        st.line_chart(df.set_index("timestamp")["value"])
    else:
        st.write("No data available")
except Exception as e:
    st.write(f"Error fetching Prometheus data: {e}")

# Predicted Failure Risks
st.header("Predicted Failure Risks")
try:
    with open("/app/models/predictor.pkl", "rb") as f:
        model = pickle.load(f)
    with open("/app/models/encoder.pkl", "rb") as f:
        le = pickle.load(f)
    conn = sqlite3.connect("/app/database/ship_maintenance.db")
    df = pd.read_sql_query("SELECT * FROM maintenance_schedules", conn)
    conn.close()
    df["equipment_encoded"] = le.transform(df["equipment"])
    df["days_until_due"] = (pd.to_datetime(df["next_due"]) - pd.to_datetime("2025-10-20")).dt.days
    X = df[["equipment_encoded", "days_until_due"]]
    df["failure_risk"] = model.predict_proba(X)[:, 1]
    st.table(df[["equipment", "task", "next_due", "failure_risk"]])
except Exception as e:
    st.write(f"Error predicting failure risks: {e}")
