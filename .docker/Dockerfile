FROM python:3.10

WORKDIR /app_bet

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


COPY pyroject.toml poetry.lock /app_bet/

RUN pip3 install --upgrade pip && pip3 install poetry && poetry install --no-cache


COPY . .
