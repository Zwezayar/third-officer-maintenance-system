import streamlit as st
import requests
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(filename="/app/logs/dashboard_audit.log", level=logging.INFO)

# Login page
def login_page():
    st.title("Third Officer Maintenance System")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password == "ThirdOfficer2025":
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Incorrect password")
    return st.session_state.get("logged_in", False)

# Fetch alerts from API or cache
def fetch_alerts():
    try:
        response = requests.get("http://api:8000/alerts/overdue", timeout=5)
        response.raise_for_status()
        alerts = response.json().get("alerts", [])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect("/app/database/ship_maintenance.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)",
                      ("alerts/overdue", str({"alerts": alerts}), timestamp))
        conn.commit()
        conn.close()
        logging.info(f"Cached response for alerts/overdue with data: {alerts}")
        return alerts, timestamp
    except requests.RequestException:
        conn = sqlite3.connect("/app/database/ship_maintenance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT value, timestamp FROM cache WHERE key = 'alerts/overdue'")
        result = cursor.fetchone()
        conn.close()
        if result:
            alerts = eval(result[0]).get("alerts", [])
            logging.info(f"Retrieved cached response for alerts/overdue from {result[1]}")
            return alerts, result[1]
        logging.warning("No cached alerts available")
        return [], None

# Main dashboard
def main_dashboard():
    st.subheader("Overdue Maintenance Tasks (SOLAS III/20)")
    if st.button("Refresh Alerts"):
        alerts, timestamp = fetch_alerts()
        if alerts:
            df = pd.DataFrame(alerts)
            st.dataframe(df)
            fig = px.bar(df, x="equipment", y="id", title=f"Overdue Tasks (Fetched: {timestamp})")
            st.plotly_chart(fig)
            logging.info(f"Displayed alerts from {timestamp}")
        else:
            st.warning("No overdue tasks available")
            logging.warning("No overdue tasks displayed")

# App entry point
if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        login_page()
    else:
        main_dashboard()