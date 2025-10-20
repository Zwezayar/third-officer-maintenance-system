import streamlit as st
import pandas as pd
import sqlite3
import pickle
import requests

st.title("Third Officer Maintenance Dashboard")

try:
    response = requests.get("http://api:8000/alerts/overdue")
    alerts = response.json()["alerts"]
    st.subheader("Overdue Maintenance Alerts")
    st.table(alerts)
except Exception as e:
    st.error(f"Error fetching alerts: {e}")

try:
    response = requests.get("http://prometheus:9090/api/v1/query?query=api_requests_total")
    if response.status_code == 200 and response.json().get("status") == "success":
        metrics = response.json()["data"]["result"]
        if metrics:
            df_metrics = pd.DataFrame([
                {"metric": m["metric"]["endpoint"], "value": float(m["value"][1])}
                for m in metrics
            ])
            st.subheader("API Request Metrics")
            st.table(df_metrics)
            st.subheader("API Requests Over Time")
            response = requests.get("http://prometheus:9090/api/v1/query_range?query=api_requests_total&start=2025-10-18T00:00:00Z&end=2025-10-20T23:59:59Z&step=300s")
            if response.status_code == 200 and response.json().get("status") == "success":
                data = response.json()["data"]["result"]
                if data:
                    df_plot = pd.DataFrame([
                        {"time": pd.to_datetime(float(t[0]), unit="s"), "value": float(t[1])}
                        for m in data for t in m["values"]
                    ])
                    st.line_chart(df_plot.set_index("time")["value"])
                else:
                    st.warning("No time-series data available")
            else:
                st.error(f"Error fetching time-series metrics: {response.text}")
        else:
            st.warning("No Prometheus metrics available")
    else:
        st.error(f"Error fetching metrics: {response.text}")
except Exception as e:
    st.error(f"Error fetching metrics: {str(e)}")

try:
    with open("/app/models/predictor.pkl", "rb") as f:
        model = pickle.load(f)
    with open("/app/models/encoder.pkl", "rb") as f:
        le = pickle.load(f)
    conn = sqlite3.connect("/app/database/ship_maintenance.db")
    df = pd.read_sql_query("SELECT * FROM maintenance_schedules", conn)
    conn.close()
    df["equipment_encoded"] = le.transform(df["equipment"])
    df["days_until_due"] = (pd.to_datetime(df["next_due"]) - pd.to_datetime("now")).dt.days
    X = df[["equipment_encoded", "days_until_due"]]
    df["failure_risk"] = model.predict_proba(X)[:, 1]
    st.subheader("Predicted Failure Risks")
    st.table(df[["equipment", "task", "next_due", "failure_risk"]])
except Exception as e:
    st.error(f"Error predicting failure risks: {e}")
