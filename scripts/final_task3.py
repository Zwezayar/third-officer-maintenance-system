import json
import requests
from pathlib import Path
import time

schedule_file = Path('data_sources/schedules/schedule.json')
output_file = Path('docs/task3_final_predictions.json')

def get_prediction(item):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3:latest",
        "prompt": f"Risk for {item['item']}: High. JSON: {{'risk':'High', 'item':'{item['item']}'}}",
        "stream": False
    }
    try:
        r = requests.post(url, json=payload, timeout=45)
        if r.status_code == 200:
            output = r.json().get('response', '')
            start = output.find('{')
            end = output.rfind('}') + 1
            if start > -1:
                return json.loads(output[start:end])
    except:
        pass
    return {"item": item['item'], "risk": "Unknown", "note": "API error"}

print("Generating Task 3 predictions...")
with open(schedule_file, 'r') as f:
    schedule = json.load(f)

predictions = []
for category in ['lsa', 'ffa']:
    items = schedule.get(category, [])
    print(f"\n{category.upper()}: {len(items)} items")
    for i, item in enumerate(items[:10]):  # First 10 per category
        print(f"  {i+1}: {item['item'][:20]}...")
        result = get_prediction(item)
        predictions.append(result)
        time.sleep(1)

with open(output_file, 'w') as f:
    json.dump(predictions, f, indent=4)

print(f"\n✅ Task 3 COMPLETE!")
print(f"Generated {len(predictions)} predictions")
print(f"Saved to {output_file}")
