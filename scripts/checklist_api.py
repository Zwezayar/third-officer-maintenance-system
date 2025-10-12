from fastapi import FastAPI
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Third Officer API")

@app.get("/")
async def root():
    return {"message": "Task 3 API - Predictions Ready", "endpoints": ["/predictions", "/schedule/lsa"]}

@app.get("/predictions")
async def get_predictions():
    pred_file = Path('docs/task3_final_predictions.json')
    if not pred_file.exists():
        return {"error": "Predictions missing", "size": 0}
    
    with open(pred_file) as f:
        data = json.load(f)
    return {
        "total": len(data) if isinstance(data, list) else len(data.get('predictions', [])),
        "predictions": data if isinstance(data, list) else data.get('predictions', []),
        "source_file": pred_file.name
    }

@app.get("/schedule/{category}")
async def get_schedule(category: str):
    sched_file = Path('data_sources/schedules/schedule.json')
    if not sched_file.exists():
        return {"error": "Schedule missing"}
    
    with open(sched_file) as f:
        data = json.load(f)
    
    schedule = data.get(category, [])
    for item in schedule:
        if 'next_due' in item:
            try:
                due = datetime.strptime(item['next_due'], '%Y-%m-%d')
                item['status'] = 'Overdue' if due < datetime.now() else 'Pending'
            except:
                item['status'] = 'Invalid'
    
    return {"category": category, "items": schedule}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
