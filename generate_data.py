import pandas as pd
from datetime import datetime, timedelta
import random

# Generate synthetic failure data
equipment = ["Lifeboat 1", "Fire Extinguisher A", "Engine Room Pump"]
tasks = ["Inspection", "Pressure Test", "Lubrication"]
data = []
for _ in range(100):
    equip = random.choice(equipment)
    task = random.choice(tasks)
    start_date = datetime.now() - timedelta(days=random.randint(30, 365))
    due_date = start_date + timedelta(days=random.randint(30, 90))
    days_overdue = (datetime.now().date() - due_date.date()).days
    failure = 1 if days_overdue > 30 or random.random() < 0.2 else 0  # Simulate failures
    data.append([equip, task, start_date.strftime("%Y-%m-%d"), due_date.strftime("%Y-%m-%d"), days_overdue, failure])

df = pd.DataFrame(data, columns=["Equipment", "Task", "Start Date", "Due Date", "Days Overdue", "Failure"])
df.to_csv("failure_data.csv", index=False)
print("Generated failure_data.csv")
