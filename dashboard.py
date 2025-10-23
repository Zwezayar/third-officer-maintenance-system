import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import time
import json
import joblib
from sklearn.preprocessing import LabelEncoder

st.title("Third Officer Maintenance Dashboard")

# Fetch maintenance schedules from API
try:
    response = requests.get("http://third-officer-maintenance-system-api-1:8000/maintenance", timeout=10)
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

# Fetch API metrics from Prometheus with retry
st.subheader("API Request Metrics")
metrics_data = []
for _ in range(5):  # Increased retries
    try:
        response = requests.get(
            "http://third-officer-maintenance-system-prometheus-1:9090/api/v1/query",
            params={"query": 'api_requests_total'},
            timeout=15
        )
        response.raise_for_status()
        metrics = response.json()["data"]["result"]
        metrics_data = [{"Endpoint": m["metric"]["endpoint"], "Requests": float(m["value"][1])} for m in metrics]
        break
    except requests.RequestException as e:
        st.warning(f"Retrying Prometheus query due to: {e}")
        time.sleep(10)
if metrics_data:
    df_metrics = pd.DataFrame(metrics_data)
    st.table(df_metrics)
else:
    st.error("Failed to fetch Prometheus metrics after retries.")

# API requests over time
st.subheader("API Requests Over Time")
chart_data = None
for _ in range(5):  # Increased retries
    try:
        response = requests.get(
            "http://third-officer-maintenance-system-prometheus-1:9090/api/v1/query_range",
            params={
                "query": 'rate(api_requests_total[5m])',
                "start": (datetime.now() - pd.Timedelta(minutes=30)).timestamp(),
                "end": datetime.now().timestamp(),
                "step": "15s"
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()["data"]["result"]
        st.write(f"Debug: Prometheus response: {json.dumps(data, indent=2)}")  # Debug output
        if data:
            times = pd.date_range(start=datetime.now() - pd.Timedelta(minutes=30), end=datetime.now(), freq="15s")
            chart_data = pd.DataFrame({"Time": times})
            for metric in data:
                endpoint = metric["metric"]["endpoint"]
                values = [float(v[1]) for v in metric["values"] if len(v) > 1]
                timestamps = [pd.to_datetime(float(v[0]), unit="s") for v in metric["values"] if len(v) > 1]
                df_temp = pd.DataFrame({"Time": timestamps, endpoint: values})
                chart_data = chart_data.merge(df_temp, on="Time", how="left")
            chart_data = chart_data.fillna(0).set_index("Time")
            if not chart_data.empty:
                st.line_chart(chart_data)
            else:
                st.write("No valid data points for chart.")
            break
        else:
            st.write("No data available for chart.")
            break
    except requests.RequestException as e:
        st.warning(f"Retrying Prometheus chart query due to: {e}")
        time.sleep(10)
if chart_data is None:
    st.error("Failed to fetch Prometheus chart data after retries.")

# AI predictions
st.subheader("Predicted Failure Risks")
try:
    model = joblib.load("failure_model.pkl")
    le_equip = joblib.load("le_equip.pkl")
    le_task = joblib.load("le_task.pkl")
    prediction_data = []
    for s in schedules:
        due_date = datetime.strptime(s[4], "%Y-%m-%d").date()
        days_overdue = (today - due_date).days
        equip_encoded = le_equip.transform([s[1]])[0]
        task_encoded = le_task.transform([s[2]])[0]
        features = pd.DataFrame([[equip_encoded, task_encoded, days_overdue]], 
                              columns=["Equipment", "Task", "Days Overdue"])
        risk = model.predict_proba(features)[0][1]  # Probability of failure
        risk_level = "High" if risk > 0.7 else "Medium" if risk > 0.3 else "Low"
        prediction_data.append([s[1], s[2], risk_level, f"{risk:.2%}"])
    if prediction_data:
        df_predictions = pd.DataFrame(prediction_data, columns=["Equipment", "Task", "Risk Level", "Failure Probability"])
        st.table(df_predictions)
    else:
        st.write("No predictions available.")
except Exception as e:
    st.error(f"Error loading AI model: {e}")
