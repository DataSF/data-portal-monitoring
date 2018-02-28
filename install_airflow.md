https://medium.com/a-r-g-o/installing-apache-airflow-on-ubuntu-aws-6ebac15db211


#airflow setup
sudo apt-get install python-pip3
pip3 install --upgrade pip

#psql
sudo -u postgres psql
CREATE ROLE airflow;
create database airflow;
 GRANT ALL PRIVILEGES on database airflow to airflow;
 ALTER ROLE airflow SUPERUSER;
 ALTER ROLE airflow CREATEDB;
 GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
ALTER USER airflow
  WITH PASSWORD 'some_password';
ALTER ROLE airflow WITH LOGIN;

ALTER USER 'airflow' WITH PASSWORD 'some_password';

 #now update the psql configs:
 ill tell return the location of the pg_hba.conf file (it's likely in /etc/postgresql/9.*/main/). Open the file with a text editor (vi, emacs or nano), and change the ipv4 address to 0.0.0.0/0 and the ipv4 connection method from md5 (password) to trust if you don't want to use a password to connect to the database. In the meantime, we also need to configure the postgresql.conf file to open the listen address to all ip addresses:
listen_addresses = '*'.
And we need to start a postgresql service
sudo service postgresql start
And any time we modify the connection information, we need to reload the postgresql service for the modification to be recognized by the service:
sudo service postgresql reload

 install the following dependencies:
sudo apt-get install libmysqlclient-dev (dependency for airflow[mysql] package)
sudo apt-get install libssl-dev (dependency for airflow[cryptograph] package)
sudo apt-get install libkrb5-dev (dependency for airflow[kerbero] package)
sudo apt-get install libsasl2-dev (dependency for airflow[hive] package):


#now time to install airflow 
#add airflow user

sudo useradd airflow
sudo passwd airflow


export AIRFLOW_HOME=/home/airflow/airflow

sudo pip2 install "airflow[async, devel, celery, crypto,password, postgres, qds, rabbitmq, slack]"


# in config file
sql_alchemy_conn = postgresql+psycopg2://airflow:somepass@127.0.0.1:5432/airflow

from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://airflow:somepass@127.0.0.1:5432/airflow')




# killing all the airflow tasks:
make sure the pid files are removed
rm airflow-scheduler.*
rm airflow-webserver.pid

ps -ef | grep airflow | awk '{print $2}' | xargs kill -9

#reset db:
airflow resetdb

#create user ==> from python cmd line interface

import airflow
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser
user = PasswordUser(models.User())
user.username = 'datasf'
user.email = 'datasf_admin@datasf.org'
user.password = 'somepass'
session = settings.Session()
session.add(user)
session.commit()
session.close()
exit()


#start up scheduler as a daemon service:
airflow scheduler -D

#start webserver as a daemon service
airflow webserver -D -p 8080


#backups
Make a pg user for backups
ALTER USER backup_admin
  WITH PASSWORD 'some password'
will call on this user in a backup script


