import json
from datetime import datetime, timedelta
from pathlib import Path

# Paths
checklist_file = Path('data_sources/checklists/checklists.json')
schedule_file = Path('data_sources/schedules/schedule.json')
schedule_file.parent.mkdir(exist_ok=True)

# Load checklists
with open(checklist_file, 'r') as f:
    checklists = json.load(f)

# Generate schedule with due dates
def generate_schedule(checklist):
    schedule = []
    for item in checklist:
        frequency = item.get('frequency', 'Weekly')
        base_due = datetime.now()
        if frequency == 'Weekly':
            next_due = base_due + timedelta(days=7)
        elif frequency == 'Monthly':
            next_due = base_due + timedelta(days=30)
        elif frequency == 'Yearly':
            next_due = base_due + timedelta(days=365)
        else:
            next_due = base_due + timedelta(days=7)
        schedule.append({
            'item': item['item'],
            'description': item['description'],
            'regulation': item['regulation'],
            'frequency': frequency,
            'next_due': next_due.strftime('%Y-%m-%d'),
            'status': 'Pending' if next_due > datetime.now() else 'Overdue'
        })
    # Sort by due date
    schedule.sort(key=lambda x: datetime.strptime(x['next_due'], '%Y-%m-%d'))
    return schedule

# Create schedules
schedules = {
    'lsa': generate_schedule(checklists.get('lsa', [])),
    'ffa': generate_schedule(checklists.get('ffa', []))
}

# Save to JSON
with open(schedule_file, 'w') as f:
    json.dump(schedules, f, indent=4)

print(f"Maintenance schedule generated at {schedule_file}")

