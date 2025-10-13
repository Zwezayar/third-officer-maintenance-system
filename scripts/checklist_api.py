from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
import json, os
from datetime import datetime, timezone

app = FastAPI(title="Third-Officer Maintenance API", version="1.1")

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
SCENARIOS_FILE = os.path.join(ROOT, "data_sources", "training", "scenarios.json")
COMPLETED_FILE = os.path.join(ROOT, "data_sources", "training", "completed_trainings.json")
PREDICTIONS_FILE = os.path.join(ROOT, "docs", "task3_final_predictions.json")

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

predictions = load_json(PREDICTIONS_FILE, [])
scenarios = load_json(SCENARIOS_FILE, {}).get("scenarios", [])
completed_trainings = load_json(COMPLETED_FILE, [])

class CompletedTraining(BaseModel):
    scenario_id: int
    crew_id: str
    notes: str = ""

@app.get("/health")
def health_check():
    return {
        "server": "running",
        "predictions": bool(predictions),
        "schedule": True,
        "checklists": True,
        "predictions_count": len(predictions)
    }

@app.get("/predictions")
def get_predictions():
    return {"predictions": predictions}

@app.get("/schedule/lsa")
def get_lsa_schedule():
    return {"schedule": "Weekly LSA checks per SOLAS III/20", "recommended_interval_days": 7}

@app.get("/training/scenarios")
def get_training_scenarios():
    return {"scenarios": scenarios}

@app.post("/crew/complete-training")
def complete_training(
    scenario_id: int = Query(..., ge=1),
    crew_id: str = Query(..., min_length=1),
    notes: str = Query("", max_length=200)
):
    scenario = next((s for s in scenarios if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    record = {
        "scenario_id": scenario_id,
        "crew_id": crew_id,
        "title": scenario.get("title"),
        "notes": notes,
        "completed_at": datetime.now(timezone.utc).isoformat()
    }
    completed_trainings.append(record)
    save_json(COMPLETED_FILE, completed_trainings)
    return {"status": "Training completed", "record": record}

@app.get("/crew/trainings")
def get_completed_trainings():
    return {"completed_trainings": completed_trainings}
