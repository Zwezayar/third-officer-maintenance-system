import json
import os
from datetime import datetime
import subprocess

# ---------- CONFIG: pre-filled for Task 4 ----------
TASK_ID = 4
TASK_NAME = "Crew Training Endpoints"
RESPONSIBLE = "ZWE"
OBJECTIVE = "Implement crew training endpoints to manage scenario-based training"
FILES_CHANGED = [
    "scripts/checklist_api.py",
    "data_sources/training/completed_trainings.json"
]
ENDPOINTS_FEATURES = [
    "GET /training/scenarios",
    "POST /crew/complete-training",
    "GET /crew/trainings"
]
TESTING_RESULTS = [
    "GET /training/scenarios returned full list of scenarios",
    "POST /crew/complete-training recorded data correctly",
    "GET /crew/trainings returned all completed training entries",
    "Server health and previous endpoints remained functional"
]
STATUS = "Completed"
NEXT_STEP = "Please generate Task 5 for the project"

def get_git_info():
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        return branch, commit
    except:
        return "unknown", "unknown"

def generate_task_report(filename=None):
    branch, commit = get_git_info()
    report = {
        "task_id": TASK_ID,
        "task_name": TASK_NAME,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "branch": branch,
        "commit": commit,
        "responsible": RESPONSIBLE,
        "objective": OBJECTIVE,
        "files_changed": FILES_CHANGED,
        "endpoints_features": ENDPOINTS_FEATURES,
        "testing_results": TESTING_RESULTS,
        "status": STATUS,
        "next_step": NEXT_STEP
    }
    if not filename:
        filename = f"task_reports/task{TASK_ID}_report.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ Task report JSON generated: {filename}")
    return report

if __name__ == "__main__":
    generate_task_report()

