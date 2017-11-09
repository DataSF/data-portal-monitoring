#!/bin/sh

#build the docker airflow image

docker build -t monitor_portal docker

#run the docker compose file to get the services up and running 
docker-compose -f docker-compose.yaml up -d