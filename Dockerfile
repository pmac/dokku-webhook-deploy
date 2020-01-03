FROM python:3.8-slim-buster

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=review_apps

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g ${GROUP_ID} dokku
RUN useradd -rmu ${USER_ID} -g dokku dokku

RUN apt-get update && \
    apt-get install -y --no-install-recommends ssh git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
CMD ["bin/run-prod"]

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./bin ./bin
COPY ./review_apps ./review_apps

USER dokku
