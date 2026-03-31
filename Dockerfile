FROM python:3.10-slim

WORKDIR /app

# Plus aucune installation système lourde !
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

<<<<<<< HEAD
EXPOSE 5000
CMD ["python", "api/app.py"]
###okay
=======
ENV PYTHONUNBUFFERED=1

>>>>>>> c8f1effa01324c533e6d8efb577ae1d63cc63f0a
