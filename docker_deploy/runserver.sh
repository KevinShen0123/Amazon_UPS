#!/bin/bash
while True
do
    python3 manage.py runserver 0.0.0.0:8000
    sleep 1
done