FROM python:3.8-slim-buster

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends ssh && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
CMD ["bin/run-prod"]

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./bin ./bin
COPY ./review_apps ./review_apps