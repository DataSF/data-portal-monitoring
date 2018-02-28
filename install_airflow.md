
# Installing airflow

See this blog article: 
https://medium.com/a-r-g-o/installing-apache-airflow-on-ubuntu-aws-6ebac15db211


## make sure you are using pip3 and python3. 
##### airflow setup
`sudo apt-get install python-pip3
pip3 install --upgrade pip`


## 1. Create a airflow user and create a db for airflow 
`sudo -u postgres psql
CREATE ROLE airflow;
create database airflow;
 GRANT ALL PRIVILEGES on database airflow to airflow;
 ALTER ROLE airflow SUPERUSER;
 ALTER ROLE airflow CREATEDB;
 GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
ALTER USER airflow
  WITH PASSWORD 'datasf_airflow';
ALTER ROLE airflow WITH LOGIN;

ALTER USER 'airflow' WITH PASSWORD 'some password';`

 ## Now update the psql configs:
 
You will need to find the location of the pg_hba.conf file (it's likely in /etc/postgresql/9.*/main/). Open the file with a text editor (vi, emacs or nano), and change the ipv4 address to 0.0.0.0/0 and the ipv4 connection method from md5 (password) to trust if you don't want to use a password to connect to the database. In the meantime, we also need to configure the postgresql.conf file to open the listen address to all ip addresses:

` listen_addresses = '*'.
And we need to start a postgresql service
sudo service postgresql start
And any time we modify the connection information, we need to reload the postgresql service for the modification to be recognized by the service:
sudo service postgresql reload `



## Install some dependecies for
install the following dependencies:
sudo apt-get install libmysqlclient-dev (dependency for airflow[mysql] package)
sudo apt-get install libssl-dev (dependency for airflow[cryptograph] package)
sudo apt-get install libkrb5-dev (dependency for airflow[kerbero] package)
sudo apt-get install libsasl2-dev (dependency for airflow[hive] package):


### now time to install airflow 

`#add airflow user
sudo useradd airflow
sudo passwd airflow
#export the airflow home dir
export AIRFLOW_HOME=/home/airflow/airflow
sudo pip2 install "airflow[async, devel, celery, crypto,password, postgres, qds, rabbitmq, slack]"`


## Modify the airflow config to use psql

`sql_alchemy_conn = postgresql+psycopg2://airflow:somepass@127.0.0.1:5432/airflow

from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://airflow:somepass@127.0.0.1:5432/airflow')  `


## Other notes:  killing all the airflow tasks:
#make sure the pid files are removed
`rm airflow-scheduler.*
rm airflow-webserver.pid`

Or check the processes:
`ps -ef | grep airflow | awk '{print $2}' | xargs kill -9`

## Resetting the postgres db:
`airflow resetdb`


## Creating an airflow user for the airflow web UI 

You will need to create user to log into the airflow web UI ==> you will do this from python cmd line interface

Do `python3`

That will bring you into the python interface
`>>> 
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
exit()`


## Restarting or starting the airflow scheduler as a daemon service:
`airflow scheduler -D`

## start airflow webserver as a daemon service
`airflow webserver -D -p 8080`


## Taking backups 
#Make a pg user for backups
`ALTER USER backup_admin
  WITH PASSWORD 'some password'
will call on this user in a backup script`


