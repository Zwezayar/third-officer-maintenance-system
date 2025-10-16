import streamlit as st
import pandas as pd
import sqlite3

# Authentication
def check_password():
    def password_entered():
        if st.session_state["password"] == "ThirdOfficer2025":
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    return True

# Database connection
def get_db():
    conn = sqlite3.connect("database/ship_maintenance.db")
    conn.row_factory = sqlite3.Row
    return conn

# Main dashboard
if check_password():
    st.title("Third Officer Maintenance Dashboard")
    st.header("STCW A-II/1 & SOLAS Compliance")

    # Maintenance Schedules
    st.subheader("Maintenance Schedules (SOLAS III/20, II-2/9)")
    conn = get_db()
    schedules = pd.read_sql_query("SELECT * FROM maintenance_schedules", conn)
    conn.close()
    st.dataframe(schedules)

    # Training Records
    st.subheader("Crew Training Records (STCW A-II/1)")
    conn = get_db()
    trainings = pd.read_sql_query("SELECT * FROM training_records", conn)
    conn.close()
    st.dataframe(trainings)

    # Compliance Summary
    st.subheader("Compliance Status")
    st.write("System aligns with STCW A-II/1, SOLAS III/20, II-2/9, MSC.428(98)")
else:
    st.error("Please enter the correct password")
