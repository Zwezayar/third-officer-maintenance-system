import json
from pathlib import Path
import subprocess
import tempfile
import os
import time

# Paths
schedule_file = Path('data_sources/schedules/schedule.json')
prediction_file = Path('docs/failure_predictions.json')
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

# Load schedule
with open(schedule_file, 'r') as f:
    schedule = json.load(f)

def predict_batch(batch_data, batch_num, max_retries=3):
    """Predict failures for a batch using temporary file input"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(batch_data, temp_file, indent=2)
        temp_path = temp_file.name
    
    for attempt in range(max_retries):
        try:
            cmd = [
                'ollama', 'run', 'aisingapore/Llama-SEA-LION-v3.5-8B-R:latest',
                f'Predict maintenance failures for batch {batch_num}: Load schedule from file {temp_path}. '
                f'Use historical data (309 lifeboat defects, 287 fire-damper failures). '
                f'Output ONLY valid JSON with "predictions" array.'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    predictions = json.loads(result.stdout.strip())
                    os.unlink(temp_path)  # Clean temp file
                    return predictions
                except json.JSONDecodeError as e:
                    print(f"JSON decode error in batch {batch_num}: {e}")
            else:
                print(f"Attempt {attempt+1} failed for batch {batch_num}: {result.stderr}")
                time.sleep(2 ** attempt)
        except subprocess.TimeoutExpired:
            print(f"Timeout in batch {batch_num}")
            time.sleep(2 ** attempt)
    
    os.unlink(temp_path)
    return {"error": f"Batch {batch_num} failed after {max_retries} attempts"}

# Process batches (5 items per batch)
all_predictions = {"predictions": [], "errors": []}
batch_size = 5

for category in ['lsa', 'ffa']:
    cat_schedule = schedule.get(category, [])
    for i in range(0, len(cat_schedule), batch_size):
        batch = cat_schedule[i:i+batch_size]
        if batch:
            batch_num = f"{category.upper()}_{i//batch_size + 1}"
            result = predict_batch(batch, batch_num)
            if "error" not in result:
                all_predictions["predictions"].extend(result.get("predictions", []))
            else:
                all_predictions["errors"].append(result)

# Save predictions
with open(prediction_file, 'w') as f:
    json.dump(all_predictions, f, indent=4)

print(f"Failure predictions saved: {len(all_predictions['predictions'])} predictions, {len(all_predictions['errors'])} errors")
print(f"Check logs/ for detailed output")

