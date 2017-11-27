# coding: utf-8
#!/usr/bin/env python


#below creates the dags and tasks for the portal monitioring tasks

import airflow
from builtins import range
from airflow.operators.bash_operator import BashOperator
from airflow.models import DAG
from datetime import timedelta
from airflow.operators.subdag_operator import SubDagOperator


#sudo pkill -9 -f "airflow scheduler"
#airflow scheduler
#airflow resetdb
# each Workflow/DAG must have a unique text identifier
WORKFLOW_DAG_ID = 'data_monitoring_workflow_dag'

# start/end times are datetime objects
# here we start execution on Jan 1st, 2017
WORKFLOW_START_DATE = airflow.utils.dates.days_ago(0)

# schedule/retry intervals are timedelta objects
# here we execute the DAGs tasks every day
WORKFLOW_SCHEDULE_INTERVAL = '*/10 * * * *'

# default arguments are applied by default to all tasks 
# in the DAG
WORKFLOW_DEFAULT_ARGS = {
    'owner': 'j9',
    'depends_on_past': False,
    'start_date': WORKFLOW_START_DATE,
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=0)
}

BASEPYTHON = "python3 "
BASEDIR = "/home/j9/data-portal-monitoring/"

# initialize the DAG
dag = DAG(
    dag_id=WORKFLOW_DAG_ID,
    start_date=WORKFLOW_START_DATE,
    schedule_interval='*/10 * * * *',
    default_args=WORKFLOW_DEFAULT_ARGS,
)


#get_datasets_cmd = "/usr/local/bin/python2 /Users/j9/Desktop/data-portal-monitoring/get_datasets.py"
#get_datasets_cmd = "python /data-portal-monitoring/get_datasets.py"
#print ('/usr/local/bin/python2 /Users/j9/Desktop/data-portal-monitoring/get_datasets.py')
get_datasets_cmd =  BASEPYTHON + BASEDIR + "get_datasets.py"
t1 = BashOperator(
        task_id= 'portal_activities',
        bash_command=get_datasets_cmd,
        dag=dag
)

#get_deleted_cmd = "/usr/local/bin/python3 /Users/j9/Desktop/data-portal-monitoring/deleted_datasets.py"
#get_deleted_cmd = "python /data-portal-monitoring/deleted_datasets.py"
get_deleted_cmd = BASEPYTHON + BASEDIR + "deleted_datasets.py" 
t2 = BashOperator(
        task_id= 'deleted_datasets',
        bash_command=get_deleted_cmd,
        dag=dag,
        depends_on_past=True
)


#get_created_cmd = "/usr/local/bin/python2 /Users/j9/Desktop/data-portal-monitoring/created_datasets.py"
#get_created_cmd = "python /data-portal-monitoring/created_datasets.py"
get_created_cmd = BASEPYTHON + BASEDIR + "created_datasets.py"
t3 = BashOperator(
        task_id= 'created_datasets',
        bash_command=get_created_cmd,
        dag=dag,
        depends_on_past=True
)


#get_stale_cmd = "python3 /Users/j9/Desktop/data-portal-monitoring/late_updated_datasets.py"
#get_stale_cmd = "python /data-portal-monitoring/late_updated_datasets.py"
get_stale_cmd = BASEPYTHON + BASEDIR + "late_updated_datasets.py"
t4 = BashOperator(
        task_id= 'stale_delayed_datasets',
        bash_command=get_stale_cmd,
        dag=dag,
        depends_on_past=True
)


DIGEST_DAG_ID = 'portal_monitoring_digest_stale_and_delayed'
dag2 = DAG(
    dag_id='data_monitoring_workflow_dag.data_monitoring_workflow_dag.digest_dag', 
    default_args=WORKFLOW_DEFAULT_ARGS,
    start_date=WORKFLOW_START_DATE,
    schedule_interval='*/59 * * * *',
 )

#stale_delayed_datasets_digest_cmd = "python2 /Users/j9/Desktop/data-portal-monitoring/digest_late_updated_datasets.py"
#stale_delayed_datasets_digest_cmd = "python /data-portal-monitoring/digest_late_updated_datasets.py"
stale_delayed_datasets_digest_cmd = BASEPYTHON + BASEDIR + "digest_late_updated_datasets.py"
t5 = BashOperator(
        task_id='stale_delayed_datasets_digest',
        bash_command=stale_delayed_datasets_digest_cmd,
        dag=dag2
)

digest = SubDagOperator(
    subdag=dag2,
    task_id= 'data_monitoring_workflow_dag.digest_dag',
    dag=dag,
)

dag >> t1
t1 >> t2 
t1 >> t3 
t1 >> t4
t1 >> digest

#airflow test data_monitoring_workflow_dag portal_activities 2017-11-27