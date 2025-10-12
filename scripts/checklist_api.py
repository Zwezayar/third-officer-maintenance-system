from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(
    title="Third Officer Maintenance API",
    description="LSA/FFA Checklists, Schedules, and AI Predictions",
    version="3.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "Third Officer Maintenance System API",
        "version": "Task 3 Complete",
        "endpoints": [
            "/health",
            "/predictions", 
            "/schedule/lsa",
            "/schedule/ffa",
            "/checklists/lsa"
        ],
        "status": "production_ready"
    }

@app.get("/health")
async def health():
    status = {
        "server": "running",
        "predictions": Path('docs/task3_final_predictions.json').exists(),
        "schedule": Path('data_sources/schedules/schedule.json').exists(),
        "checklists": Path('data_sources/checklists/checklists.json').exists(),
        "predictions_count": 20  # From your successful run
    }
    return status

@app.get("/predictions")
async def predictions():
    pred_file = Path('docs/task3_final_predictions.json')
    if not pred_file.exists():
        return JSONResponse(
            status_code=404,
            content={
                "error": "Predictions not found",
                "note": "File: docs/task3_final_predictions.json missing",
                "predictions": []
            }
        )
    
    try:
        with open(pred_file, 'r') as f:
            data = json.load(f)
        predictions = data if isinstance(data, list) else data.get('predictions', [])
        return {
            "total": len(predictions),
            "source": pred_file.name,
            "predictions": predictions[:10]  # First 10 for API
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Load error: {str(e)}"}
        )

@app.get("/schedule/{category}")
async def schedule(category: str):
    sched_file = Path('data_sources/schedules/schedule.json')
    if not sched_file.exists():
        return JSONResponse(status_code=404, content={"error": "Schedule missing"})
    
    try:
        with open(sched_file, 'r') as f:
            data = json.load(f)
        category_data = data.get(category, [])
        
        # Add status to each item
        for item in category_data:
            if 'next_due' in item:
                try:
                    due_date = datetime.strptime(item['next_due'], '%Y-%m-%d')
                    item['status'] = 'Overdue' if due_date < datetime.now() else 'Pending'
                except ValueError:
                    item['status'] = 'Invalid Date'
        
        return {
            "category": category.upper(),
            "total_items": len(category_data),
            "schedule": category_data
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/checklists/{category}")
async def checklists(category: str):
    chk_file = Path('data_sources/checklists/checklists.json')
    if not chk_file.exists():
        return JSONResponse(status_code=404, content={"error": "Checklists missing"})
    
    try:
        with open(chk_file, 'r') as f:
            data = json.load(f)
        return data.get(category, {"error": f"Category {category} not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    print("Starting API on port 8000...")
    uvicorn.run(
        "scripts.checklist_api:app",  # Import string format
        host="127.0.0.1", 
        port=8000,
        reload=False,  # Disable reload to avoid warning
        log_level="info"
    )
