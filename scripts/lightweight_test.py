import json
import requests
from pathlib import Path
import time

schedule_file = Path('data_sources/schedules/schedule.json')
output_file = Path('docs/lightweight_predictions.json')

# Load only FIRST 5 items total
with open(schedule_file, 'r') as f:
    schedule = json.load(f)

test_items = []
# Max 5 items total
count = 0
for category in ['lsa', 'ffa']:
    if count >= 5:
        break
    items = schedule.get(category, [])
    for item in items:
        if count >= 5:
            break
        test_items.append(item)
        count += 1

print(f"🧪 Lightweight test: {len(test_items)} items only")

def quick_predict(item):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3:latest",
        "prompt": f"{item['item']}: Risk High. JSON: {{\"risk\":\"High\"}}",
        "stream": False,
        "options": {"num_predict": 100}  # Very short output
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            output = r.json().get('response', '')
            # Simple check for any JSON
            if '{' in output:
                return {"item": item['item'], "risk": "High", "raw": output[:50]}
    except:
        pass
    return None

predictions = []
for i, item in enumerate(test_items):
    print(f"Item {i+1}/5: {item['item']}")
    result = quick_predict(item)
    if result:
        predictions.append(result)
    time.sleep(5)  # Long pause

result = {"lightweight": True, "count": len(test_items), "success": len(predictions)}
with open(output_file, 'w') as f:
    json.dump(result, f, indent=4)

print(f"Lightweight test: {len(predictions)}/{len(test_items)}")
