
# coding: utf-8
#!/usr/bin/env python
from Utils import *
from ConfigUtils import *
from PostgresStuff import *
from PandasUtils import *
from MonitorPortal import *


def updateStaleDelayedDatasets(conn, update_time_interval):
  #get the datasets that are stale or delayed in the past time interval.
  #Looks at the max time in the table, and then looks 12 hours from that max time. 
  #This makes it a little bit more fault tolerant, in the event that server stops or there
  #is some kind of outage in the monitoring
  qry = """
    select z.*, zz.late_as_of  from 
    (
      SELECT 
        a.time, a.datasetid, name, pub_health, updated_at, pub_freq, days_last_updt, pub_dept,  created_at
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
    ORDER by days_last_updt desc
    """ 
  print tmp_stale_datasets_qry

  tmp_updated_datasets = PostgresStuff.commitQry(conn, tmp_stale_datasets_qry )

  #insert the created datasets into the update dataset table. 
  #Only insert the records if the tmp created are newer that the lastest record in 
  #the created dataset table or if the the datasetid isn't in the created dataset table

  updted_datasets_qry = """
    INSERT into late_updated_datasets
      (  time, datasetid, name, last_checked, pub_health, updated_at, 
          pub_freq, days_last_updt, pub_dept, created_at
      )
      SELECT NOW(), tu.datasetid, pa.name, tu.last_checked, pa.pub_health, pa.updated_at,  
        pa.pub_freq, pa.days_last_updt, pa.pub_dept,pa.created_at
      FROM portal_activity pa 
      JOIN tmp_late_updated tu
        ON pa.datasetid = tu.datasetid and tu.last_checked = pa.time
      LEFT JOIN(
        SELECT datasetid, last(last_checked, last_checked) as max_last_checked, updated_at
        FROM  late_updated_datasets
        GROUP BY datasetid, updated_at
      ) ud 
      ON ud.datasetid = tu.datasetid
      WHERE  
      (
          (ud.datasetid IS NULL) OR 
          (ud.updated_at < pa.updated_at and ud.datasetid = tu.datasetid)    
   
      ) 
    """
  updted_datasets  = PostgresStuff.commitQry(conn, updted_datasets_qry)
  return updted_datasets


def main():
  curr_full_path = FileUtils.getCurrentDirFullPath()
  config_fn = 'portal_activity_job_config.yaml'
  cI =  ConfigUtils(curr_full_path+ "/configs/" , config_fn)
  configItems = cI.getConfigs()
  configItems['config_dir'] = curr_full_path+ "/" + configItems['config_dir']
  configItems['curr_full_path']  = curr_full_path
  db_ini = configItems['config_dir'] + configItems['database_config']
  db_config = PostgresStuff.load_config(filename=db_ini)
  conn_alq, meta_alq =PostgresStuff.connect_alq(db_config)
  conn = PostgresStuff.connect()
  db_tbl = configItems['activity_table']
  insert_late_updated = updateStaleDelayedDatasets(conn, configItems['activity']['update']['time_interval'])
  print insert_late_updated
  created_datasets  = MonitorPortal.generateActivityReport(conn_alq, configItems, 'update')
  if (not (created_datasets)):
    print "**** No new created datasets in the past " + configItems['activity']['update']['time_interval'] + "*****"
    exit (0)
  datasetid_notified = MonitorPortal.generateEmail(conn_alq, configItems, 'update', created_datasets)
  updted_notified_cnt = MonitorPortal.updateNotifiedDatasetIds(conn, configItems, 'update', datasetid_notified)
  print "******Notfied that " +str(updted_notified_cnt) + " datasets are late or stale****" 
  print "******Updated" + str(updted_notified_cnt) + " rows in the late_updated_dataset table****" 


  


if __name__ == "__main__":
    main()