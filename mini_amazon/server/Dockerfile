FROM ubuntu:20.04
RUN mkdir /code
ADD . /code/
WORKDIR /code

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN ls 
RUN apt-get update 
RUN apt-get -y install build-essential libpqxx-dev postgresql 
RUN apt-get install -y autoconf automake libtool curl make g++

# install protobuf

RUN apt-get -yq install protobuf-compiler