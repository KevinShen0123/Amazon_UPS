FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /frontcode
RUN apt-get update && apt-get install -y postgresql-client
WORKDIR /frontcode
ADD . /frontcode/
#RUN chmod 777 initfront.sh
CMD ["chmod 777 /frontcode/initfront.sh"]
#RUN chmod 777 runserver.sh
CMD ["chmod 777 /frontcode/runserver.sh"]
RUN pip install django-model-utils
RUN pip install psycopg2
CMD ["bash","/frontcode/runserver.sh"]