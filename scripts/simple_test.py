import json
import requests
from pathlib import Path

schedule_file = Path('data_sources/schedules/schedule.json')
with open(schedule_file, 'r') as f:
    schedule = json.load(f)

test_item = schedule.get('lsa', [{}])[0] if schedule.get('lsa') else {}

print(f"Testing: {test_item.get('item', 'No item')}")

url = "http://localhost:11434/api/generate"
payload = {
    "model": "llama3:latest",
    "prompt": f"Item: {test_item.get('item')}\nOutput: {{'risk':'Medium'}}",
    "stream": False
}

r = requests.post(url, json=payload, timeout=45)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    result = r.json()
    output = result.get('response', '')
    print(f"Response: {output}")
    
    start = output.find('{')
    end = output.rfind('}') + 1
    if start > -1:
        pred = json.loads(output[start:end])
        print("Success:", pred)
    else:
        print("No JSON")
else:
    print("Error:", r.text)
