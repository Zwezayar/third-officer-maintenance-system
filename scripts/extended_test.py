import json
import requests
from pathlib import Path
import time

schedule_file = Path('data_sources/schedules/schedule.json')
with open(schedule_file, 'r') as f:
    schedule = json.load(f)

test_item = None
for cat in ['lsa', 'ffa']:
    if schedule.get(cat) and len(schedule[cat]) > 0:
        test_item = schedule[cat][0]
        break

if not test_item:
    print("No items!")
    exit(1)

print(f"Testing: {test_item['item']}")
print("Waiting for model to be fully responsive...")

url = "http://localhost:11434/api/generate"
payload = {
    "model": "aisingapore/Llama-SEA-LION-v3.5-8B-R:latest",
    "prompt": f"Item: {test_item['item']}\nOutput JSON: {{\"risk\": \"Medium\", \"status\": \"ready\"}}",
    "stream": False,
    "options": {"temperature": 0.0, "num_predict": 200}
}

start_time = time.time()
try:
    print("Sending request (120s timeout)...")
    response = requests.post(url, json=payload, timeout=120)
    elapsed = time.time() - start_time
    print(f"Response time: {elapsed:.1f}s")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        output = result.get('response', '').strip()
        print(f"Output length: {len(output)}")
        print(f"Output: {output}")
        
        # Extract JSON
        start = output.find('{')
        end = output.rfind('}') + 1
        if start != -1 and end > start:
            prediction = json.loads(output[start:end])
            print("✅ JSON SUCCESS!")
            print(json.dumps(prediction, indent=2))
        else:
            print("❌ No JSON found")
    else:
        print(f"❌ Error: {response.text}")
except requests.exceptions.Timeout:
    print("⏰ Still timing out - model not ready or server issue")
except Exception as e:
    print(f"❌ Error: {e}")
