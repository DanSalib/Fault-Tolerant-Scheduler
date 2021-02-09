#!/bin/bash
sudo rm -rf logs/*
sudo docker-compose down
sudo docker-compose up -d --build
pip3 install -r ./slave/requirements.txt
sudo python3 populate_db.py
