
#!/bin/bash


#restart up script
#run when server reboots or when you want to restart airflow scheduler and webserver

#remove pids files
rm /home/airflow/airflow/airflow-scheduler.*
rm /home/airflow/airflow/airflow-webserver.pid

#kill related processes:
ps -ef | grep airflow | awk '{print $2}' | xargs kill -9

#start scheduler
airflow scheduler -D

#start the webserver
airflow webserver -D &>/dev/null
#default port is 8080


#this will run as a crontab job when the server gets restarted.
#https://askubuntu.com/questions/814/how-to-run-scripts-on-start-up

#@reboot /home/airflow/airflow/restart_airflow.sh