def call_sea_lion(prompt, max_retries=3):
    # Warmup call to ensure model is loaded
    warmup_payload = {
        "model": MODEL,
        "prompt": "Test connection",
        "stream": False,
        "options": {"temperature": 0.1}
    }
    try:
        warmup_response = requests.post(OLLAMA_URL, json=warmup_payload, timeout=30)
        warmup_response.raise_for_status()
        print("Model warmup successful")
    except Exception as e:
        print(f"Warmup failed: {e}")
    
    for attempt in range(max_retries):
        try:
            payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 1000}
            }
            response = requests.post(OLLAMA_URL, json=payload, timeout=120)  # Increased to 120s
            response.raise_for_status()
            result = response.json()
            
            output = result.get('response', '').strip()
            print(f"Raw output length: {len(output)} characters")
            print(f"Output preview: {output[:200]}...")
            
            if output:
                start = output.find('{')
                end = output.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = output[start:end]
                    return json.loads(json_str)
            
            print(f"Attempt {attempt + 1}: Empty or invalid JSON")
            time.sleep(5)  # Fixed delay between retries
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1}: Timeout - server may be loading model")
            time.sleep(10)
        except Exception as e:
            print(f"Attempt {attempt + 1}: Error - {e}")
            time.sleep(5)
    
    return {"error": "All retries failed"}import json
import requests
from pathlib import Path
import time

# Paths
schedule_file = Path('data_sources/schedules/schedule.json')
prediction_file = Path('docs/failure_predictions.json')
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / 'prediction_log.txt'

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "aisingapore/Llama-SEA-LION-v3.5-8B-R:latest"

# Load schedule
with open(schedule_file, 'r') as f:
    schedule = json.load(f)

def call_sea_lion(prompt, max_retries=3):
    """Direct API call to SEA-LION with retry"""
    for attempt in range(max_retries):
        try:
            payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 1000}
            }
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            output = result.get('response', '').strip()
            if output:
                start = output.find('{')
                end = output.rfind('}') + 1
                if start != -1 and end > start:
                    return json.loads(output[start:end])
            print(f"Attempt {attempt + 1}: Empty response")
            time.sleep(2 ** attempt)
        except Exception as e:
            print(f"Attempt {attempt + 1}: Error - {e}")
            time.sleep(2 ** attempt)
    return {"error": "Failed after retries"}

def create_simple_prompt(item):
    """Simplified prompt for one item"""
    return f"Predict failure for this item: {item['item']} ({item['description']}, {item['frequency']} frequency, due {item['next_due']}). Historical risks: 309 lifeboat defects, 287 fire-damper failures. Output ONLY JSON: {{\"risk_level\": \"High\", \"mitigation\": \"Weekly check\", \"regulation\": \"SOLAS III/20\"}}"

# Process item by item
all_predictions = {"predictions": [], "errors": []}
lsa_schedule = schedule.get('lsa', [])
ffa_schedule = schedule.get('ffa', [])

# Process LSA
for i, item in enumerate(lsa_schedule):
    prompt = create_simple_prompt(item)
    result = call_sea_lion(prompt)
    if "error" not in result:
        all_predictions["predictions"].append(result)
    else:
        all_predictions["errors"].append({"item": item['item'], "error": result})
    print(f"LSA item {i+1}/{len(lsa_schedule)} processed")

# Process FFA
for i, item in enumerate(ffa_schedule):
    prompt = create_simple_prompt(item)
    result = call_sea_lion(prompt)
    if "error" not in result:
        all_predictions["predictions"].append(result)
    else:
        all_predictions["errors"].append({"item": item['item'], "error": result})
    print(f"FFA item {i+1}/{len(ffa_schedule)} processed")

# Save predictions
with open(prediction_file, 'w') as f:
    json.dump(all_predictions, f, indent=4)

with open(log_file, 'w') as f:
    f.write(json.dumps(all_predictions, indent=4))

print(f"Predictions saved: {len(all_predictions['predictions'])} successful, {len(all_predictions['errors'])} errors")
print(f"Log: {log_file}")
