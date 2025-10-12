import json
import requests
from pathlib import Path

# Load schedule
schedule_file = Path('data_sources/schedules/schedule.json')
with open(schedule_file, 'r') as f:
    schedule = json.load(f)

# Get first LSA item (or FFA if no LSA)
test_item = None
if schedule.get('lsa') and len(schedule['lsa']) > 0:
    test_item = schedule['lsa'][0]
elif schedule.get('ffa') and len(schedule['ffa']) > 0:
    test_item = schedule['ffa'][0]

if not test_item:
    print("❌ No schedule items found!")
    exit(1)

print(f"🧪 Testing prediction for: {test_item['item']}")
print(f"   Frequency: {test_item['frequency']}")
print(f"   Due: {test_item['next_due']}")

# Direct API call
url = "http://localhost:11434/api/generate"
payload = {
    "model": "aisingapore/Llama-SEA-LION-v3.5-8B-R:latest",
    "prompt": f"""Maintenance risk analysis:

Item: {test_item['item']}
Description: {test_item.get('description', 'Standard inspection')}
Frequency: {test_item['frequency']}
Due Date: {test_item['next_due']}

Predict:
1. Risk level (High/Medium/Low)
2. Recommended action/mitigation
3. Relevant SOLAS regulation

Output ONLY valid JSON (no explanations):
{{"item": "{test_item['item']}", "risk_level": "High", "mitigation": "Weekly visual inspection", "regulation": "SOLAS III/20"}}""",
    "stream": False,
    "options": {
        "temperature": 0.0,
        "num_predict": 400
    }
}

try:
    print("📡 Sending API request...")
    response = requests.post(url, json=payload, timeout=60)
    
    print(f"📊 HTTP Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        output = result.get('response', '').strip()
        
        print(f"📝 Raw Output Length: {len(output)} characters")
        print(f"📄 Output Preview: {output[:150]}...")
        
        # Extract JSON from response
        start_idx = output.find('{')
        end_idx = output.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = output[start_idx:end_idx]
            try:
                prediction = json.loads(json_str)
                print("✅ SUCCESS - Valid JSON Prediction!")
                print(f"Prediction Details:")
                print(json.dumps(prediction, indent=2))
                
                # Save result
                with open('docs/single_test_result.json', 'w') as f:
                    json.dump({
                        "success": True,
                        "item": test_item['item'],
                        "prediction": prediction,
                        "raw_output": output
                    }, f, indent=4)
                print("💾 Saved to docs/single_test_result.json")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                print(f"JSON attempt: {json_str[:100]}...")
        else:
            print("❌ No JSON braces found in output")
            print("Full output:")
            print(output)
            
            # Save raw output for debugging
            with open('docs/single_test_raw.json', 'w') as f:
                json.dump({"success": False, "raw_output": output}, f, indent=4)
    else:
        print(f"❌ HTTP Error Response:")
        print(response.text)
        
        # Save error for debugging
        with open('docs/single_test_error.json', 'w') as f:
            json.dump({"success": False, "error": response.text}, f, indent=4)
            
except requests.exceptions.Timeout:
    print("⏰ Request timed out - model may still be loading")
except Exception as e:
    print(f"💥 Unexpected error: {e}")
