import json
from pathlib import Path

# Directories
extracted_dir = Path('data_sources/extracted/text')
output_dir = Path('data_sources/checklists')
output_dir.mkdir(exist_ok=True)

def parse_checklist(file_path, category):
    checklist = []
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()

    for line in lines:
        line = line.strip()
        if line:
            # Detect items with bullets or dashes
            if '-' in line or '■' in line:
                parts = line.split('–') if '–' in line else [line, ""]
                item = parts[0].strip(' ■')
                desc = parts[1].strip() if len(parts) > 1 else ""
                checklist.append({
                    "category": category,
                    "item": item,
                    "description": desc,
                    "regulation": "SOLAS III/20" if "lifeboat" in line.lower() else "SOLAS II-2",
                    "due": "Weekly" if "weekly" in line.lower() else "Monthly"
                })
    return checklist

# Parse both checklists
lsa_checklist = parse_checklist(extracted_dir / 'lsa_checklist.txt', 'lsa')
ffa_checklist = parse_checklist(extracted_dir / 'ffa_checklist.txt', 'ffa')

# Save JSON
checklists = {"lsa": lsa_checklist, "ffa": ffa_checklist}
with open(output_dir / 'checklists.json', 'w') as f:
    json.dump(checklists, f, indent=4)

print("Checklists digitized at data_sources/checklists/checklists.json")

