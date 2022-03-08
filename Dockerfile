# syntax=docker/dockerfile:1
FROM python:3

RUN pip install --upgrade pip

RUN adduser -D myuser
USER myuser

COPY --chown=myuser:myuser requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

COPY --chown=myuser:myuser . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
