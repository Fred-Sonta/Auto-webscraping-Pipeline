FROM python:3.10-slim

WORKDIR /app

# Plus aucune installation système lourde !
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

