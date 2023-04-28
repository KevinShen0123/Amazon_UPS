FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /frontcode
WORKDIR /frontcode
ADD . /frontcode/
RUN chmod 777 initfront.sh
RUN chmod 777 runserver.sh
RUN pip install django-model-utils
RUN pip install psycopg2
RUN /frontcode/initfront.sh