import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import joblib

# Load data
df = pd.read_csv("failure_data.csv")

# Preprocess
le_equip = LabelEncoder()
le_task = LabelEncoder()
df["Equipment"] = le_equip.fit_transform(df["Equipment"])
df["Task"] = le_task.fit_transform(df["Task"])

# Features and target
X = df[["Equipment", "Task", "Days Overdue"]]
y = df["Failure"]

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression(max_iter=1000)  # Increased iterations for convergence
model.fit(X_train, y_train)

# Save model and encoders
joblib.dump(model, "failure_model.pkl")
joblib.dump(le_equip, "le_equip.pkl")
joblib.dump(le_task, "le_task.pkl")

print(f"Model trained with accuracy: {model.score(X_test, y_test):.2f}")
