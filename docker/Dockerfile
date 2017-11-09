# docker rm $(docker ps -a -q -f status=exited)
#docker images

#Download base image ubuntu 16.04
FROM ubuntu:16.04

# Update the base image
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y dist-upgrade
RUN apt-get install -y git libcurl4-openssl-dev

# Install dependencies

RUN apt-get -y install python-pip python-dev libffi-dev 

RUN apt-get install git

RUN git clone https://github.com/DataSF/data-portal-monitoring.git

RUN pip install pyyaml pandas openpyxl sqlalchemy psycopg2 airflow 
RUN pip install airflow password

#pip install pycurl

EXPOSE 8080