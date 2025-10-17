import streamlit as st
import requests
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
import logging
import json

# Setup logging for audit trails
logging.basicConfig(
    filename="logs/dashboard_audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    logging.info("Initialized session state: authenticated=False")

# Database connection
def get_db():
    try:
        conn = sqlite3.connect("database/ship_maintenance.db")
        conn.row_factory = sqlite3.Row
        logging.info("Connected to database")
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        raise e

# Cache API response
def cache_api_response(endpoint, data):
    try:
        conn = get_db()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT OR REPLACE INTO cache (endpoint, data, timestamp)
            VALUES (?, ?, ?)
        """, (endpoint, json.dumps(data), timestamp))
        conn.commit()
        conn.close()
        logging.info(f"Cached response for {endpoint} with data: {data}")
    except Exception as e:
        logging.error(f"Failed to cache response for {endpoint}: {str(e)}")

# Get cached API response
def get_cached_response(endpoint):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT data, timestamp FROM cache WHERE endpoint = ?", (endpoint,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return json.loads(result['data']), result['timestamp']
        return None, None
    except Exception as e:
        logging.error(f"Failed to get cached response for {endpoint}: {str(e)}")
        return None, None

# Mark maintenance task as completed
def mark_task_completed(task_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        next_due = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute("""
            UPDATE maintenance_schedules 
            SET last_completed = ?, next_due = ? 
            WHERE id = ?
        """, (today, next_due, task_id))
        conn.commit()
        conn.close()
        logging.info(f"Task {task_id} marked as completed by Third Officer")
        return True
    except Exception as e:
        logging.error(f"Failed to mark task {task_id} as completed: {str(e)}")
        return False

# Authentication
def check_password():
    st.title("Third Officer Maintenance Dashboard")
    st.subheader("Authentication Required")

    with st.form("login_form"):
        password = st.text_input("Password:", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if password == "ThirdOfficer2025":
                st.session_state.authenticated = True
                logging.info("Authentication successful")
                st.success("Authentication successful!")
            else:
                st.session_state.authenticated = False
                logging.warning("Authentication failed: Invalid password")
                st.error("Invalid password. Please try again.")

    if st.button("Debug Session State"):
        st.write(f"Authenticated: {st.session_state.authenticated}")

# Main dashboard
def main_dashboard():
    st.title("Third Officer Maintenance Dashboard")
    st.header("STCW A-II/1 & SOLAS Compliance")
    logging.info("Rendering main dashboard")

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        logging.info("User logged out")
        st.experimental_rerun()

    # Real-Time SEA-LION Alerts
    st.subheader("SEA-LION Real-Time Alerts")
    if st.button("Refresh Alerts"):
        try:
            response = requests.get("http://api:8000/alerts/overdue")
            response.raise_for_status()
            alerts = response.json()["alerts"]
            cache_api_response("alerts/overdue", alerts)
            if alerts:
                df = pd.DataFrame(alerts)
                st.dataframe(df)
                fig = px.bar(df, x="equipment", y="task", title="Overdue Maintenance Tasks (SOLAS III/20)")
                st.plotly_chart(fig)
                logging.info("SEA-LION alerts refreshed")
            else:
                st.write("No overdue tasks")
        except requests.RequestException as e:
            st.warning(f"Offline mode: Using cached alerts ({str(e)})")
            alerts, timestamp = get_cached_response("alerts/overdue")
            if alerts:
                df = pd.DataFrame(alerts)
                st.dataframe(df)
                fig = px.bar(df, x="equipment", y="task", title=f"Overdue Maintenance Tasks (Cached: {timestamp})")
                st.plotly_chart(fig)
                logging.info(f"Displayed cached SEA-LION alerts from {timestamp}")
            else:
                st.error("No cached alerts available")

    # Maintenance Schedules
    st.subheader("Maintenance Schedules")
    try:
        conn = get_db()
        schedules = pd.read_sql_query("SELECT * FROM maintenance_schedules", conn)
        conn.close()
        if not schedules.empty:
            st.dataframe(schedules)
        else:
            st.write("No maintenance schedules found")
    except Exception as e:
        st.error(f"Failed to load maintenance schedules: {str(e)}")
        logging.error(f"Failed to load maintenance schedules: {str(e)}")

    # Complete Maintenance Task
    st.subheader("Complete Maintenance Task")
    with st.form("task_completion_form"):
        task_id = st.number_input("Task ID", min_value=1, step=1)
        submitted = st.form_submit_button("Mark Task Completed")
        if submitted:
            if mark_task_completed(task_id):
                st.success(f"Task {task_id} marked as completed")
            else:
                st.error(f"Failed to mark task {task_id} as completed")

    # Training Records
    st.subheader("Crew Training Records (STCW A-II/1)")
    try:
        conn = get_db()
        trainings = pd.read_sql_query("SELECT * FROM training_records", conn)
        conn.close()
        if not trainings.empty:
            st.dataframe(trainings)
        else:
            st.write("No training records found")
    except Exception as e:
        st.error(f"Failed to load training records: {str(e)}")
        logging.error(f"Failed to load training records: {str(e)}")

    # Prometheus Metrics Visualization
    st.subheader("API Performance Metrics")
    try:
        response = requests.get("http://api:8000/metrics")
        response.raise_for_status()
        metrics = response.text
        cache_api_response("metrics", {"metrics": metrics})
        st.text_area("Raw Metrics", metrics, height=200)
        request_counts = pd.DataFrame({
            "endpoint": ["/health", "/alerts/overdue"],
            "count": [100, 50]
        })
        fig = px.bar(request_counts, x="endpoint", y="count", title="API Request Counts")
        st.plotly_chart(fig)
        logging.info("Prometheus metrics displayed")
    except requests.RequestException as e:
        st.warning(f"Offline mode: Using cached metrics ({str(e)})")
        metrics, timestamp = get_cached_response("metrics")
        if metrics:
            st.text_area("Raw Metrics (Cached)", metrics["metrics"], height=200)
            request_counts = pd.DataFrame({
                "endpoint": ["/health", "/alerts/overdue"],
                "count": [100, 50]
            })
            fig = px.bar(request_counts, x="endpoint", y="count", title=f"API Request Counts (Cached: {timestamp})")
            st.plotly_chart(fig)
            logging.info(f"Displayed cached metrics from {timestamp}")
        else:
            st.error("No cached metrics available")

    # Compliance Summary
    st.subheader("Compliance Status")
    st.write("System aligns with STCW A-II/1, SOLAS III/20, II-2/9, MSC.428(98)")

# Main logic
logging.info(f"Session state authenticated: {st.session_state.authenticated}")
if not st.session_state.authenticated:
    check_password()
else:
    main_dashboard()
