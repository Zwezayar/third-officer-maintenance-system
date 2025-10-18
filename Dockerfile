FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y curl && pip install --no-cache-dir -r requirements.txt

COPY scripts/ scripts/
COPY data_sources/ data_sources/
COPY database/ database/
COPY logs/ logs/
COPY dashboard/ dashboard/
COPY task_reports/ task_reports/

EXPOSE 8000 8501

CMD ["uvicorn", "scripts.checklist_api:app", "--host", "0.0.0.0", "--port", "8000"]
