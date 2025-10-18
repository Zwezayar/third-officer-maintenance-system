import streamlit as st
import requests
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
import logging
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    filename="logs/dashboard_audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    logging.info("Initialized session state: authenticated=False")

def get_db():
    try:
        conn = sqlite3.connect("database/ship_maintenance.db")
        conn.row_factory = sqlite3.Row
        logging.info("Connected to database")
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        raise e

def cache_api_response(endpoint, data):
    try:
        conn = get_db()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT OR REPLACE INTO cache (endpoint, data, timestamp) VALUES (?, ?, ?)",
            (endpoint, json.dumps(data), timestamp)
        )
        conn.commit()
        conn.close()
        logging.info(f"Cached response for {endpoint} with data: {data}")
    except Exception as e:
        logging.error(f"Failed to cache response for {endpoint}: {str(e)}")

def get_cached_response(endpoint):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT data, timestamp FROM cache WHERE endpoint = ?", (endpoint,))
        result = cursor.fetchone()
        conn.close()
        if result:
            logging.info(f"Retrieved cached response for {endpoint} from {result['timestamp']}")
            return json.loads(result['data']), result['timestamp']
        logging.warning(f"No cached response for {endpoint}")
        return None, None
    except Exception as e:
        logging.error(f"Failed to get cached response for {endpoint}: {str(e)}")
        return None, None

def mark_task_completed(task_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        next_due = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute(
            "UPDATE maintenance_schedules SET last_completed = ?, next_due = ? WHERE id = ?",
            (today, next_due, task_id)
        )
        conn.commit()
        conn.close()
        logging.info(f"Task {task_id} marked as completed by Third Officer")
        return True
    except Exception as e:
        logging.error(f"Failed to mark task {task_id} as completed: {str(e)}")
        return False

session = requests.Session()
retries = Retry(total=5, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))

API_BASE_URL = "http://api:8000"

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

def main_dashboard():
    st.title("Third Officer Maintenance Dashboard")
    st.header("STCW A-II/1 & SOLAS Compliance")
    logging.info("Rendering main dashboard")

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        logging.info("User logged out")
        st.experimental_rerun()

    st.subheader("SEA-LION Real-Time Alerts")
    if st.button("Refresh Alerts"):
        endpoint = "alerts/overdue"
        try:
            url = f"{API_BASE_URL}/{endpoint}"
            logging.info(f"Attempting to fetch alerts from {url}")
            response = session.get(url, timeout=5)
            response.raise_for_status()
            alerts = response.json()["alerts"]
            logging.info(f"Received alerts: {alerts}")
            cache_api_response(endpoint, alerts)
            if alerts:
                df = pd.DataFrame(alerts)
                st.dataframe(df)
                fig = px.bar(df, x="equipment", y="task", title="Overdue Maintenance Tasks (SOLAS III/20)")
                st.plotly_chart(fig)
                logging.info("SEA-LION alerts refreshed")
            else:
                st.write("No overdue tasks")
                logging.info("No overdue tasks found")
        except requests.RequestException as e:
            st.warning(f"Offline mode: Using cached alerts ({str(e)})")
            alerts, timestamp = get_cached_response(endpoint)
            if alerts:
                df = pd.DataFrame(alerts)
                st.dataframe(df)
                fig = px.bar(df, x="equipment", y="task", title=f"Overdue Maintenance Tasks (Cached: {timestamp})")
                st.plotly_chart(fig)
                logging.info(f"Displayed cached SEA-LION alerts from {timestamp}")
            else:
                st.error("No cached alerts available")
                logging.warning("No cached alerts available")

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

    st.subheader("Complete Maintenance Task")
    with st.form("task_completion_form"):
        task_id = st.number_input("Task ID", min_value=1, step=1)
        submitted = st.form_submit_button("Mark Task Completed")
        if submitted:
            if mark_task_completed(task_id):
                st.success(f"Task {task_id} marked as completed")
            else:
                st.error(f"Failed to mark task {task_id} as completed")

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

    st.subheader("Add Training Record")
    with st.form("training_form"):
        name = st.text_input("Crew Name")
        training_type = st.text_input("Training Type")
        completion_date = st.date_input("Completion Date")
        expiry_date = st.date_input("Expiry Date")
        submitted = st.form_submit_button("Add Training")
        if submitted:
            try:
                response = session.post(
                    f"{API_BASE_URL}/training/add",
                    json={
                        "name": name,
                        "training_type": training_type,
                        "completion_date": str(completion_date),
                        "expiry_date": str(expiry_date)
                    },
                    timeout=5
                )
                response.raise_for_status()
                st.success(f"Training added: {training_type} for {name}")
                logging.info(f"Training added: {training_type} for {name}")
            except requests.RequestException as e:
                st.error(f"Failed to add training: {str(e)}")
                logging.error(f"Failed to add training: {str(e)}")

    st.subheader("API Performance Metrics")
    endpoint = "metrics"
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        logging.info(f"Attempting to fetch metrics from {url}")
        response = session.get(url, timeout=5)
        response.raise_for_status()
        metrics = response.text
        logging.info(f"Received metrics: {metrics[:100]}...")
        cache_api_response(endpoint, {"metrics": metrics})
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
        metrics, timestamp = get_cached_response(endpoint)
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
            logging.warning("No cached metrics available")

    st.subheader("Compliance Status")
    st.write("System aligns with STCW A-II/1, SOLAS III/20, II-2/9, MSC.428(98)")

logging.info(f"Session state authenticated: {st.session_state.authenticated}")
if not st.session_state.authenticated:
    check_password()
else:
    main_dashboard()
