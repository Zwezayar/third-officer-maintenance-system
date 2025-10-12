import json
from pathlib import Path

# Path to checklists
checklist_file = Path('data_sources/checklists/checklists.json')

# Check if file exists
if not checklist_file.exists():
    print(f"Error: {checklist_file} not found. Run Task 2 parser first.")
    exit(1)

# Load JSON
with open(checklist_file, 'r') as f:
    checklists = json.load(f)

# Print summary
print("Checklists loaded successfully!")
print(f"LSA items: {len(checklists.get('lsa', []))}")
print(f"FFA items: {len(checklists.get('ffa', []))}")

