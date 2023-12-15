FROM python:3.10

WORKDIR /app_bet

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
