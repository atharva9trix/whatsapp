# FROM python:3.11-slim

# WORKDIR /app

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 9000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]


FROM python:3.11-slim

WORKDIR /app

RUN pip install fastapi uvicorn requests

COPY main.py .

CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "9000"]
