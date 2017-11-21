
# coding: utf-8
#!/usr/bin/env python
from Utils import *
from ConfigUtils import *
from PostgresStuff import *
from PandasUtils import *
from MonitorPortal import *


def getFirstRun(conn):
  qry = '''
    SELECT  COUNT(*) from (
      SELECT datasetid, count(*) from portal_activity 
        GROUP BY datasetid
        having count(*) > 1
    )z
  '''
  results =  PostgresStuff.select_records(conn, qry)
  return results[0][0]

def updateCreatedDatasets(conn, create_time_interval):
  #get the datasets that were created in the past time interval.
  #Also references the deleted table to find instances where a dataset has been created, deleted, and then created
  #This makes it a little bit more fault tolerant, in the event that server stops or there
  #is some kind of outage in the monitoring
  tmp_create_datasets_qry = """
    DROP TABLE if exists tmp_created;

    CREATE TABLE tmp_created AS 
    SELECT a.datasetid,   a.first_seen, c.deleted_last_seen, b.last_seen, 
    a.first_seen - c.deleted_last_seen as time_btw_deleted_and_first_seen
      FROM  
      (
          SELECT datasetid, max_time, last(time, time) as first_seen
          FROM portal_activity
                LEFT JOIN (
                    SELECT MAX(TIME) AS max_time FROM portal_activity
                )m ON 1=1
          WHERE time > m.max_time - interval '%s'
          GROUP BY datasetid, max_time
        ) a
        LEFT JOIN 
        ( 
      SELECT datasetid as datasetid, last(time, time) as last_seen
            FROM portal_activity
                LEFT JOIN (
                    SELECT MAX(TIME) AS max_time FROM portal_activity
                )m ON 1=1
            WHERE time < m.max_time - interval '%s'
            GROUP BY datasetid
         ) b
        ON a.datasetid = b.datasetid
        LEFT JOIN 
        (
         SELECT datasetid, last_seen as deleted_last_seen
         FROM deleted_datasets
        ) c
        ON b.datasetid = c.datasetid 
        WHERE (b.datasetid is NULL) or (deleted_last_seen < first_seen) 
  """  % ( create_time_interval,  create_time_interval)
  tmp_deleted_datasets = PostgresStuff.commitQry(conn, tmp_create_datasets_qry)

  #insert the created datasets into the create dataset table. 
  #Only insert the records if the tmp created are newer that the lastest record in 
  #the created dataset table or if the the datasetid isn't in the created dataset table

  created_datasets_qry = """
    INSERT INTO created_datasets
      (time, datasetid, name, first_seen, created_at, pub_dept, pub_freq,
       deleted_last_seen, time_btw_deleted_and_first_seen
      )
      SELECT 
        NOW() AT TIME ZONE 'UTC', tc.datasetid, pa.name, tc.first_seen, pa.created_at,  pa.pub_dept, pa.pub_freq, 
        tc.deleted_last_seen, tc.time_btw_deleted_and_first_seen
      FROM portal_activity pa 
      JOIN tmp_created tc
      ON pa.datasetid = tc.datasetid and tc.first_seen = pa.time
      LEFT JOIN(
        SELECT datasetid, last(first_seen, first_seen) as max_first_seen
        FROM  created_datasets
        GROUP BY datasetid
      )dd 
      ON dd.datasetid = tc.datasetid
      WHERE ( 
        (dd.datasetid IS NULL) OR 
        ( tc.first_seen < dd.max_first_seen and dd.datasetid = tc.datasetid)
      ) 
    """
  created_datasets = PostgresStuff.commitQry(conn, created_datasets_qry)
  return created_datasets


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
  first_run = getFirstRun(conn)
  if first_run == 0:
    print ("****First RUN! No new created datasets in the past " + configItems['activity']['create']['time_interval'] + "*****")
    exit (0)
  insert_created = updateCreatedDatasets(conn, configItems['activity']['create']['time_interval'])
  #print insert_created
  created_datasets  = MonitorPortal.generateActivityReport(conn_alq, configItems, 'create')
  if (not (created_datasets)):
    print ("**** No new created datasets in the past " + configItems['activity']['create']['time_interval'] + "*****")
    exit (0)
  datasetid_notified = MonitorPortal.generateEmail(conn_alq, configItems, 'create', created_datasets)
  updted_notified_cnt = MonitorPortal.updateNotifiedDatasetIds(conn, configItems, 'create', datasetid_notified)
  print ("******Notfied that " +str(updted_notified_cnt) + " datasets were created****" )
  print ("******Updated " + str(updted_notified_cnt) + " rows in the created_dataset table****")



  


if __name__ == "__main__":
    main()