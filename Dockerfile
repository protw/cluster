# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080

CMD python cluster_web.py

## Build Docker image
#    $ docker build --tag python-docker .
## Run image as container
#    $ docker run -p 8080:8080 python-docker
## Running in browser on http://localhost:8080