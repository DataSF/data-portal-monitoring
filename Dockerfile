#Download base image ubuntu 16.04
FROM ubuntu:16.04

# Update the base image
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y dist-upgrade

# Install dependencies
RUN apt-get -y install python-pip python-dev libffi-dev 

RUN apt-get install git

RUN git pull https://github.com/DataSF/data-portal-monitoring.git

RUN pip install yaml pandas openpyxl pycurl sqlalchemy python-psycopg2