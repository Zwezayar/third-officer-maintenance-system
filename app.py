import streamlit as st
import requests
from datetime import datetime

# ------------------------------
# Config
# ------------------------------
BASE_URL = "http://127.0.0.1:8000"

# ------------------------------
# Page Setup
# ------------------------------
st.set_page_config(page_title="Third Officer Dashboard", layout="wide")
st.title("⚓ Third Officer Maintenance Dashboard")

# ------------------------------
# Health Status
# ------------------------------
st.subheader("Ship System Health")
try:
    health = requests.get(f"{BASE_URL}/health").json()
    st.success(f"Status: {health.get('status', 'Unknown')}")
    st.info(f"Uptime: {health.get('uptime', 'Unknown')}")
    st.caption(f"Last checked: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
except Exception as e:
    st.error(f"Failed to fetch health: {e}")

# ------------------------------
# Maintenance Schedule
# ------------------------------
st.subheader("Maintenance Schedule")
try:
    schedule = requests.get(f"{BASE_URL}/schedule/lsa").json()
    for item in schedule.get("schedules", []):
        st.write(f"**{item['equipment']}**: Next due {item['next_due']} (Last completed {item['last_completed']})")
except Exception as e:
    st.error(f"Failed to fetch schedule: {e}")

# ------------------------------
# SEA-LION Alerts
# ------------------------------
st.subheader("SEA-LION Alerts")
try:
    alerts = requests.get(f"{BASE_URL}/alerts").json()
    if alerts.get("alerts"):
        for alert in alerts["alerts"]:
            alert_type = alert["type"]
            msg = alert["message"]
            if alert_type == "critical":
                st.error(f"❗ {msg}")
            elif alert_type == "warning":
                st.warning(f"⚠️ {msg}")
            else:
                st.info(f"ℹ️ {msg}")
    else:
        st.success("No active alerts")
except Exception as e:
    st.error(f"Failed to fetch alerts: {e}")

# ------------------------------
# Checklist Items
# ------------------------------
st.subheader("Daily Checklist")
try:
    checklist = requests.get(f"{BASE_URL}/checklist").json()
    for task in checklist.get("checklist", []):
        st.checkbox(task)
except Exception as e:
    st.error(f"Failed to fetch checklist: {e}")

# ------------------------------
# Crew Trainings
# ------------------------------
st.subheader("Crew Trainings")
try:
    trainings = requests.get(f"{BASE_URL}/crew/trainings").json()
    for training in trainings.get("completed_trainings", []):
        crew_id = training["crew_id"]
        scenario_id = training["scenario_id"]
        completed = training["completed"]
        st.write(f"Crew {crew_id} - Scenario {scenario_id}: {'✅ Completed' if completed else '❌ Not Completed'}")
except Exception as e:
    st.error(f"Failed to fetch crew trainings: {e}")

# ------------------------------
# Complete Training Button
# ------------------------------
st.subheader("Mark Training as Completed")
crew_input = st.text_input("Crew ID", "")
scenario_input = st.number_input("Scenario ID", min_value=1, step=1)
if st.button("Mark Completed"):
    if crew_input:
        try:
            resp = requests.post(f"{BASE_URL}/crew/complete-training",
                                 params={"crew_id": crew_input, "scenario_id": scenario_input})
            st.success(resp.json().get("status", "Training completed"))
        except Exception as e:
            st.error(f"Failed to mark training completed: {e}")
    else:
        st.warning("Please enter a Crew ID")

