FROM python:3.12

WORKDIR /app

RUN pip install --upgrade pip && pip install poetry