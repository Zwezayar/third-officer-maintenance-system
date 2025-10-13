FROM python:3.9-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ scripts/
COPY data_sources/ data_sources/
COPY database/ database/
COPY logs/ logs/
COPY dashboard/ dashboard/

EXPOSE 8000 8501
CMD ["uvicorn", "scripts.checklist_api:app", "--host", "0.0.0.0", "--port", "8000"]
