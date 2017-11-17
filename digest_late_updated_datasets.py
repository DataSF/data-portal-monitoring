
# coding: utf-8
#!/usr/bin/env python
from Utils import *
from ConfigUtils import *
from PostgresStuff import *
from PandasUtils import *
from MonitorPortal import *


def digestStaleDelayedDatasets(conn_alq, configItems, activity):
  #get the datasets that are stale or delayed in the past time interval.
  #Looks at the max time in the table, and then looks 12 hours from that max time. 
  #This makes it a little bit more fault tolerant, in the event that server stops or there
  #is some kind of outage in the monitoring
  digest_qry = """
    select z.time, z.datasetid, z.name,  z.pub_dept, z.pub_health, z.updated_at, z.pub_freq, CAST(z.days_last_updt as varchar),  z.created_at, zz.late_as_of  from 
    (
      SELECT 
        a.time as time, a.datasetid as datasetid, name, pub_health, updated_at, pub_freq, days_last_updt, pub_dept, created_at
      FROM 
      (
        SELECT
          datasetid,  last(time, time) as time
        FROM portal_activity
        GROUP BY datasetid
      ) a       
      JOIN 
      (
      SELECT
        time, datasetid, name, pub_health, updated_at, pub_freq, CAST(coalesce(days_last_updt, '-9999') AS integer) as days_last_updt,  pub_dept, created_at
        FROM portal_activity
      )b
      ON a.datasetid =  b.datasetid and b.time = a.time
    ) z
    JOIN 
    (
      SELECT 
        a.datasetid, pub_health, time as late_as_of
      FROM
      (
        SELECT
        datasetid, last(time, time) as last_checked
        FROM late_updated_datasets
      GROUP BY datasetid
      ) a
      JOIN (
        SELECT datasetid, pub_health, time
        FROM late_updated_datasets
      )b
      ON a.datasetid =b.datasetid and a.last_checked =b.time
      ORDER by late_as_of, pub_health desc
    )zz
    ON z.datasetid = zz.datasetid 
    WHERE z.pub_health = 'Stale' or z.pub_health = 'Delayed'
    ORDER by  z.pub_dept , z.pub_health ASC 
    """ 
  report_items = MonitorPortal.generateActivityReport(conn_alq, configItems, activity, qry=digest_qry)
  return report_items

 
  #updted_datasets  = PostgresStuff.commitQry(conn, updted_datasets_qry)
  #return updted_datasets


def main():
  curr_full_path = FileUtils.getCurrentDirFullPath()
  config_fn = 'portal_activity_job_config.yaml'
  cI =  ConfigUtils(curr_full_path+ "/configs/" , config_fn)
  configItems = cI.getConfigs()
  configItems['config_dir'] = curr_full_path+ "/" + configItems['config_dir']
  configItems['curr_full_path']  = curr_full_path
  db_ini = configItems['config_dir'] + configItems['database_config']
  conn_alq, meta_alq =PostgresStuff.connect_alq(db_ini)
  conn = PostgresStuff.connect(db_ini)
  db_tbl = configItems['activity_table']
  digest_items = digestStaleDelayedDatasets(conn_alq, configItems, 'stale_delayed_digest')
  if (not (digest_items)):
    print ("**** No digest items " + configItems['activity']['update']['time_interval'] + "*****")
    exit (0)
  datasetid_notified = MonitorPortal.generateEmail(conn_alq, configItems, 'stale_delayed_digest', digest_items)
 

  


if __name__ == "__main__":
    main()