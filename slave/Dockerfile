FROM ubuntu:18.04
WORKDIR /


RUN apt-get update -y && \
  apt-get install -y

RUN apt install -y python3.7

RUN apt install -y python3-pip

COPY ./slave ./slave
COPY ./models ./slave/models

RUN pip3 install -r ./slave/requirements.txt

ENV FLASK_APP=app.py

EXPOSE 8080

CMD ["python3", "./slave/main.py"]