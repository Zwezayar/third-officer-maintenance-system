import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import sqlite3
import json

st.title("Third Officer Maintenance Dashboard")

# Fetch maintenance schedules from API
try:
    response = requests.get("http://third-officer-maintenance-system-api-1:8000/maintenance")
    response.raise_for_status()
    schedules = response.json()["schedules"]
except requests.RequestException as e:
    st.error(f"Error fetching maintenance data: {e}")
    schedules = []

# Overdue maintenance alerts
st.subheader("Overdue Maintenance Alerts")
today = date.today()
overdue = []
for s in schedules:
    due_date = datetime.strptime(s[4], "%Y-%m-%d").date()
    if due_date <= today:
        overdue.append(s)
if overdue:
    df = pd.DataFrame(overdue, columns=["ID", "Equipment", "Task", "Start Date", "Due Date"])
    st.table(df)
else:
    st.write("No overdue tasks.")

# Fetch API metrics from Prometheus
try:
    response = requests.get("http://third-officer-maintenance-system-prometheus-1:9090/api/v1/query", params={"query": 'api_requests_total'})
    response.raise_for_status()
    metrics = response.json()["data"]["result"]
    metrics_data = [{"Endpoint": m["metric"]["endpoint"], "Requests": float(m["value"][1])} for m in metrics]
    st.subheader("API Request Metrics")
    df_metrics = pd.DataFrame(metrics_data)
    st.table(df_metrics)
except requests.RequestException as e:
    st.error(f"Error fetching Prometheus data: {e}")

# API requests over time
st.subheader("API Requests Over Time")
try:
    response = requests.get("http://third-officer-maintenance-system-prometheus-1:9090/api/v1/query_range", params={
        "query": 'rate(api_requests_total[5m])',
        "start": (datetime.now() - pd.Timedelta(minutes=30)).timestamp(),
        "end": datetime.now().timestamp(),
        "step": "15s"
    })
    response.raise_for_status()
    data = response.json()["data"]["result"]
    if data:
        times = pd.date_range(start=datetime.now() - pd.Timedelta(minutes=30), end=datetime.now(), freq="15s")
        values = [float(v["value"][1]) for v in data[0]["values"]]
        chart_data = pd.DataFrame({"Time": times[:len(values)], "Rate": values})
        st.line_chart(chart_data.set_index("Time"))
    else:
        st.write("No data available for chart.")
except requests.RequestException as e:
    st.error(f"Error fetching Prometheus chart data: {e}")

# Placeholder for AI predictions (to be implemented)
st.subheader("Predicted Failure Risks")
st.write("AI model not yet implemented.")
