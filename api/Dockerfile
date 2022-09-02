FROM python:3.10

LABEL maintainer "Sean Thompson <sean@speckledbanana.com>"

RUN apt-get update

RUN mkdir /api

RUN WORKDIR /api

COPY . /api

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_ENV="docker"

EXPOSE 5000