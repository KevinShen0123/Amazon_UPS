#!/bin/bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py makemigrations amazon
python3 manage.py migrate amazon

while [ "1"=="1" ]
do
    sleep 3;
    # python3 manage.py migrate
    # res="$?"
done

