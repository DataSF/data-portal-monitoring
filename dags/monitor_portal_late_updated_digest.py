import airflow
from builtins import range
from airflow.operators.bash_operator import BashOperator
from airflow.models import DAG
from datetime import timedelta
#from airflow.operators.subdag_operator import SubDagOperator
from airflow.operators.latest_only_operator import LatestOnlyOperator
from airflow.utils.trigger_rule import TriggerRule


# schedule/retry intervals are timedelta objects
# here we execute the DAGs tasks every day
WORKFLOW_START_DATE = airflow.utils.dates.days_ago(0)

# default arguments are applied by default to all tasks 
# in the DAG
WORKFLOW_DEFAULT_ARGS = {
    'owner': 'j9',
    'depends_on_past': False,
    'start_date': WORKFLOW_START_DATE,
    'email_on_failure': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=0),
    'max_active_runs' : 1,
}

BASEPYTHON = "python3 "
BASEDIR = "/home/j9/data-portal-monitoring/"


#run thje digest every 12 hours
dag2 = DAG(
    dag_id='late_updated_digest_dag', 
    default_args=WORKFLOW_DEFAULT_ARGS,
    start_date=WORKFLOW_START_DATE,
    schedule_interval='0 */12 * * *',
 )

#stale_delayed_datasets_digest_cmd = "python2 /Users/j9/Desktop/data-portal-monitoring/digest_late_updated_datasets.py"
#stale_delayed_datasets_digest_cmd = "python /data-portal-monitoring/digest_late_updated_datasets.py"
stale_delayed_datasets_digest_cmd = BASEPYTHON + BASEDIR + "digest_late_updated_datasets.py"
t5 = BashOperator(
        task_id='stale_delayed_datasets_digest',
        bash_command=stale_delayed_datasets_digest_cmd,
        dag=dag2
)

get_datasets_cmd =  BASEPYTHON + BASEDIR + "get_datasets.py"
t11 = BashOperator(
        task_id= 'portal_activities',
        bash_command=get_datasets_cmd,
        dag=dag2
)
latest_only2 = LatestOnlyOperator(task_id='latest_only2', dag=dag2)
t11.set_upstream(latest_only2)
t5.set_upstream(t11)
