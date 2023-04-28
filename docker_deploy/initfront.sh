#!/bin/bash
python3 manage.py makemigrations
python3 manage.py migrate
echo "data migrate starting"
res="$?"
while [ "$res" != "0" ]
do
    sleep 3;
    python3 manage.py migrate
    res="$?"
done