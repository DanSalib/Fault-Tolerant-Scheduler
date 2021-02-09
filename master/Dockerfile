FROM ubuntu:18.04
WORKDIR /


RUN apt-get update -y && \
  apt-get install -y

RUN apt install -y python3.7

RUN apt install -y python3-pip

COPY ./master ./master
COPY ./models ./master/models

RUN pip3 install -r ./master/requirements.txt

ENV FLASK_APP=app.py

EXPOSE 8080