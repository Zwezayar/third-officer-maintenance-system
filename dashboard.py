import streamlit as st
import pandas as pd
import sqlite3
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
    metrics = response.json()["data"]["result"]
    if metrics:
        df_metrics = pd.DataFrame([
            {"metric": m["metric"]["endpoint"], "value": float(m["value"][1])}
            for m in metrics
        ])
        st.subheader("API Request Metrics")
        st.table(df_metrics)
        st.subheader("API Requests Over Time")
        response = requests.get("http://prometheus:9090/api/v1/query_range?query=api_requests_total&start=2025-10-18T00:00:00Z&end=2025-10-20T23:59:59Z&step=15s")
        data = response.json()["data"]["result"]
        if data:
            df_plot = pd.DataFrame([
                {"time": pd.to_datetime(float(t[0]), unit="s"), "value": float(t[1])}
                for m in data for t in m["values"]
            ])
            st.line_chart(df_plot.set_index("time")["value"])
    else:
        st.warning("No Prometheus metrics available")
except Exception as e:
    st.error(f"Error fetching metrics: {e}")

conn = sqlite3.connect("/app/database/ship_maintenance.db")
conn.close()
