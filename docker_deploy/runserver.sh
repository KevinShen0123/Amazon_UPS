#!/bin/bash
echo "Waiting for PostgreSQL to be ready..."

until PGPASSWORD=20230101 psql -h "db" -U "postgres" -c '\q'; do
  echo "PostgreSQL not ready, waiting..."
  sleep 2
done

echo "PostgreSQL ready, starting data migration."

echo "data migrate starting"
python3 manage.py makemigrations
python3 manage.py migrate

echo "server is running"
#while True
#do
#    python3 manage.py runserver 0.0.0.0:8000
#    sleep 1
#done
python manage.py runserver 0.0.0.0:8000