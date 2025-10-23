import pandas as pd
import random
from datetime import datetime, timedelta

equipment = ["Lifeboat 1", "Fire Extinguisher A", "Engine Room Pump"]
tasks = ["Inspection", "Pressure Test", "Lubrication"]
data = []
for _ in range(200):
    equip = random.choice(equipment)
    task = random.choice(tasks)
    start_date = datetime.now() - timedelta(days=random.randint(30, 365))
    due_date = start_date + timedelta(days=random.randint(30, 90))
    days_overdue = (datetime.now().date() - due_date.date()).days
    failure_prob = min(0.9, 0.2 + (days_overdue / 30) * 0.3 if days_overdue > 0 else 0.1)
    failure = 1 if random.random() < failure_prob else 0
    data.append([equip, task, start_date.strftime("%Y-%m-%d"), due_date.strftime("%Y-%m-%d"), days_overdue, failure])

df = pd.DataFrame(data, columns=["Equipment", "Task", "Start Date", "Due Date", "Days Overdue", "Failure"])
df.to_csv("failure_data.csv", index=False)
print("Generated failure_data.csv")
