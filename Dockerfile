FROM python:3.9-slim
LABEL authors="IcySugar"

WORKDIR /app

ENV PYTHONUNBUFFERED=0

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && \
    python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]