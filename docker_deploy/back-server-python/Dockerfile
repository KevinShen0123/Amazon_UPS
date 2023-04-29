FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
RUN apt-get install apt
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y postgresql-client
WORKDIR /code
ADD . /code/
#RUN chmod 777 initfront.sh
CMD ["chmod 777 /code/initfront.sh"]
#RUN chmod 777 runserver.sh
RUN pip install google
RUN pip install protobuf==3.20.0
RUN pip install psycopg2
CMD ["chmod 777 /code/runback.sh"]
CMD ["bash","/code/runback.sh"]