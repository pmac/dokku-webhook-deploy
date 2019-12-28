FROM python:3.8-slim-buster

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
CMD ["bin/run-prod"]
COPY ./bin ./bin

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./review_apps.py ./settings.py ./