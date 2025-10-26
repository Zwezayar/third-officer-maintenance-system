import streamlit as st
import pandas as pd
import os
from weasyprint import HTML
import requests

st.title("Third Officer Maintenance System")
st.write("Manage maintenance schedules and export reports for compliance with STCW A-II/1.")

storage_types = ["Deck Maintenance", "Safety Equipment", "Navigation Equipment"]
storage_type = st.selectbox("Select Storage Type", storage_types)

storage_files = {
    "Deck Maintenance": ["deck_schedule.xlsx", "deck_inspection.pdf"],
    "Safety Equipment": ["safety_checks.csv", "lifeboat_maintenance.xlsx"],
    "Navigation Equipment": ["radar_logs.xlsx", "gps_maintenance.csv"]
}

selected_storage_file = st.selectbox(f"Select {storage_type} File", storage_files[storage_type])

file_path = os.path.join("data", selected_storage_file)
if os.path.exists(file_path):
    if selected_storage_file.endswith(('.xlsx', '.xls')):
        df_storage = pd.read_excel(file_path)
    elif selected_storage_file.endswith('.csv'):
        df_storage = pd.read_csv(file_path)
    elif selected_storage_file.endswith('.pdf'):
        df_storage = None
        st.write("PDF file selected. Display not supported, but export is available.")
    else:
        df_storage = None
        st.error("Unsupported file format")
    if df_storage is not None:
        st.write(f"{storage_type} Data")
        st.dataframe(df_storage)
else:
    st.error(f"File {file_path} not found")

if st.button(f"Export {storage_type} File to PDF"):
    if selected_storage_file.endswith(('.xlsx', '.xls', '.csv')):
        try:
            html_content = df_storage.to_html()
            HTML(string=html_content).write_pdf(f"{storage_type.lower().replace(' ', '_')}.pdf")
            st.success(f"Exported to {storage_type.lower().replace(' ', '_')}.pdf")
        except Exception as e:
            st.error(f"Error exporting to PDF: {e}")
    else:
        st.error("PDF export not supported for PDF files")

st.write("Fetch Maintenance Schedules from FastAPI")
if st.button("Get Maintenance Schedules"):
    try:
        response = requests.get("http://localhost:8001/maintenance")
        if response.status_code == 200:
            schedules = response.json().get("schedules", [])
            if schedules:
                df_schedules = pd.DataFrame(schedules, columns=["ID", "Equipment", "Task", "Start Date", "Due Date"])
                st.write("Maintenance Schedules")
                st.dataframe(df_schedules)
            else:
                st.warning("No schedules found")
        else:
            st.error(f"Failed to fetch schedules: {response.status_code}")
    except requests.RequestException as e:
        st.error(f"Error connecting to FastAPI: {e}")

st.write("AI-Powered Maintenance Insights")
query = st.text_input("Ask about maintenance procedures (e.g., 'How to inspect lifeboats?')")
if st.button("Ask AI"):
    if query:
        try:
            response = requests.post("http://localhost:11434/api/generate", json={"model": "llama3", "prompt": query})
            if response.status_code == 200:
                result = response.json().get("response", "No response from AI")
                st.write("AI Response:", result)
            else:
                st.error(f"Failed to get AI response: {response.status_code}")
        except requests.RequestException as e:
            st.error(f"Error connecting to Ollama: {e}")
    else:
        st.warning("Please enter a query")
