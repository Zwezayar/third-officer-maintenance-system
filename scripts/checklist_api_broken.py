from fastapi import FastAPI
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Third Officer Maintenance API")

@app.get("/")
async def root():
    return {"message": "Third Officer Maintenance System API", "version": "Task 3"}

@app.get("/checklists/{category}")
async def get_checklist(category: str):
    file = Path('data_sources/checklists/checklists.json')
    if not file.exists():
        return {"error": "Checklists not found"}
    with open(file) as f:
        data = json.load(f)
    return data.get(category, {"error": f"{category} not found"})

@app.get("/schedule/{category}")
async def get_schedule(category: str):
    file = Path('data_sources/schedules/schedule.json')
    if not file.exists():
        return {"error": "Schedule not found"}
    with open(file) as f:
        data = json.load(f)
    schedule = data.get(category, [])
    for item in schedule:
        due = datetime.strptime(item['next_due'], '%Y-%m-%d')
        item['status'] = 'Overdue' if due < datetime.now() else 'Pending'
    return schedule

@app.get("/predictions")
async def get_predictions():
Path("docs/task3_final_predictions.json")')
    if not file.exists():
        return {"error": "Predictions not found", "note": "Run task3_llama3_predictions.py"}
    with open(file) as f:
        return json.load(f)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
