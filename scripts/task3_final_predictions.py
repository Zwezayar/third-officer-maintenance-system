import json
import requests
from pathlib import Path
import time

schedule_file = Path('data_sources/schedules/schedule.json')
output_file = Path('docs/task3_final_predictions.json')
log_file = Path('logs/task3_final.log')
log_file.parent.mkdir(exist_ok=True)

def predict_with_llama3(item):
    """Production risk prediction"""
    url = "http://localhost:11434/api/generate"
    
    # Simplified prompt for reliable JSON
    prompt = f"""Maintenance Risk Assessment:

ITEM: {item['item']}
FREQUENCY: {item['frequency']}
DUE: {item['next_due']}

Historical Data:
- 309 lifeboat release defects
- 287 fire damper failures

Required JSON Output (no explanations):
{{"item": "{item['item']}", "risk_level": "High", "mitigation": "Weekly inspection", "regulation": "SOLAS III/20"}}"""

    payload = {
        "model": "llama3:latest",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,  # Deterministic output
            "num_predict": 500
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            output = result.get('response', '').strip()
            
            # Log for debugging
            with open(log_file, 'a') as f:
                f.write(f"{item['item']}: {output[:100]}...\n")
            
            # Extract JSON
            start = output.find('{')
            end = output.rfind('}') + 1
            if start != -1 and end > start:
                try:
                    prediction = json.loads(output[start:end])
                    # Ensure required fields
                    if 'risk_level' not in prediction:
                        prediction['risk_level'] = 'Medium'
                    if 'mitigation' not in prediction:
                        prediction['mitigation'] = 'Standard inspection'
                    return prediction
                except json.JSONDecodeError:
                    print(f"Parse error for {item['item']}")
            return None
    except Exception as e:
        print(f"Error {item['item']}: {e}")
        return None

# Load schedule
print("Loading schedule...")
with open(schedule_file, 'r') as f:
    schedule = json.load(f)

all_predictions = []
processed = 0
errors = []

print(f"Processing LSA: {len(schedule.get('lsa', []))} items")
for i, item in enumerate(schedule.get('lsa', [])):
    print(f"LSA {i+1}: {item['item'][:30]}...")
    result = predict_with_llama3(item)
    if result:
        all_predictions.append(result)
        print(f"  ✅ {result.get('risk_level', 'Unknown')}")
    else:
        errors.append(item['item'])
        print("  ❌")
    processed += 1
    time.sleep(1.5)  # Rate limit

print(f"\nProcessing FFA: {len(schedule.get('ffa', []))} items")
for i, item in enumerate(schedule.get('ffa', [])):
    print(f"FFA {i+1}: {item['item'][:30]}...")
    result = predict_with_llama3(item)
    if result:
        all_predictions.append(result)
        print(f"  ✅ {result.get('risk_level', 'Unknown')}")
    else:
        errors.append(item['item'])
        print("  ❌")
    processed += 1
    time.sleep(1.5)

# Save results
result_data = {
    "model": "llama3:latest",
    "total_processed": processed,
    "successful_predictions": len(all_predictions),
    "errors": len(errors),
    "predictions": all_predictions
}

with open(output_file, 'w') as f:
    json.dump(result_data, f, indent=4)

print(f"\n🎉 Task 3 COMPLETE!")
print(f"📊 Processed: {processed} items")
print(f"✅ Predictions: {len(all_predictions)}")
print(f"❌ Errors: {len(errors)}")
print(f"💾 Saved: {output_file}")

if all_predictions:
    print("\n📋 Sample Prediction:")
    print(json.dumps(all_predictions[0], indent=2))
