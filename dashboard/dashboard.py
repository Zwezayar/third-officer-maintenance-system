import streamlit as st
import requests
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(filename="/app/logs/dashboard_audit.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Log action to audit_log table and file
def log_action(action, user, details):
    try:
        conn = sqlite3.connect("/app/database/ship_maintenance.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (action, user, timestamp, details)
            VALUES (?, ?, ?, ?)
        """, (action, user, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), details))
        conn.commit()
        conn.close()
        logging.info(f"Audit: {action} by {user}: {details}")
    except Exception as e:
        logging.error(f"Error logging action {action}: {str(e)}")

# Login page
def login_page():
    st.title("Third Officer Maintenance System")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password == "ThirdOfficer2025":
            st.session_state.logged_in = True
            log_action("login_success", "user", "User logged in successfully")
            st.success("Logged in successfully!")
            st.rerun()
        else:
            log_action("login_failure", "user", "Incorrect password entered")
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
        log_action("fetch_alerts", "user", f"Cached {len(alerts)} alerts")
        return alerts, timestamp
    except requests.RequestException as e:
        log_action("fetch_alerts_offline", "user", f"API unavailable, using cache: {str(e)}")
        conn = sqlite3.connect("/app/database/ship_maintenance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT value, timestamp FROM cache WHERE key = 'alerts/overdue'")
        result = cursor.fetchone()
        conn.close()
        if result:
            alerts = eval(result[0]).get("alerts", [])
            log_action("fetch_alerts_cache", "user", f"Retrieved {len(alerts)} cached alerts from {result[1]}")
            return alerts, result[1]
        log_action("fetch_alerts_no_cache", "user", "No cached alerts available")
        return [], None

# Main dashboard
def main_dashboard():
    st.header("Overdue Maintenance Tasks (SOLAS III/20)")
    if st.button("Refresh Alerts"):
        alerts, timestamp = fetch_alerts()
        if alerts:
            df = pd.DataFrame(alerts)
            st.dataframe(df)
            fig = px.bar(df, x="equipment", y="id", title=f"Overdue Tasks ({'Fetched' if timestamp and timestamp > datetime.now().strftime('%Y-%m-%d %H:%M:%S') else 'Cached'}: {timestamp})")
            st.plotly_chart(fig)
            log_action("display_alerts", "user", f"Displayed {len(alerts)} alerts from {timestamp}")
        else:
            st.warning("No overdue tasks available")
            log_action("display_no_alerts", "user", "No overdue tasks displayed")

# App entry point
if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        login_page()
    else:
        main_dashboard()
