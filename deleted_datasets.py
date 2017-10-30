
# coding: utf-8
#!/usr/bin/env python
from Utils import *
from ConfigUtils import *
from PostgresStuff import *

def updateDeletedDatasets(conn, deleted_time_iterval):
  #get the datasets that were deleted in the past time interval.
  #Rather than using NOW(), this query grabs the max time from the portal_activity table
  #This makes it a little bit more fault tolerant, in the event that server stops or there
  #is some kind of outage in the monitoring
  tmp_deleted_datasets_qry =  """
		DROP TABLE if exists tmp_deleted;

		CREATE TABLE tmp_deleted AS 
			SELECT a.datasetid, last_seen
      FROM  
      ( 
          SELECT datasetid as datasetid, last(time, time) as last_seen
          FROM portal_activity
                LEFT JOIN (
                    SELECT MAX(TIME) AS max_time FROM portal_activity
                )m ON 1=1
          WHERE time < m.max_time - interval '60 minutes'
          GROUP BY datasetid
        ) a 
        LEFT JOIN 
        (
          SELECT datasetid, max_time, last(time, time)
          FROM portal_activity
                LEFT JOIN (
                    SELECT MAX(TIME) AS max_time FROM portal_activity
                )m ON 1=1
          WHERE time > m.max_time - interval '%s'
          GROUP BY datasetid, max_time
        ) b
        ON a.datasetid = b.datasetid
        WHERE b.datasetid is NULL """ % (deleted_time_iterval)
  tmp_deleted_datasets = PostgresStuff.commitQry(conn, tmp_deleted_datasets_qry)

  #insert the deleted datasets into the deleted dataset table. 
  #Only insert the records if the tmp deleted are newer that the lastest record in 
  #the deleted dataset table or if the the datasetid isn't in the deleted dataset table

  deleted_datasets_qry = """
    INSERT INTO deleted_datasets
      (time, datasetid, name, last_seen, pub_dept, pub_freq, created_at)
      SELECT 
        NOW(), td.datasetid, pa.name, td.last_seen, pa.pub_dept, pa.pub_freq, pa.created_at
      FROM portal_activity pa 
      JOIN tmp_deleted td 
      ON pa.datasetid = td.datasetid and td.last_seen = pa.time
      LEFT JOIN(
        SELECT datasetid, last(last_seen, last_seen) as max_last_seen
        FROM  deleted_datasets
        GROUP BY datasetid
      )dd 
      ON dd.datasetid = td.datasetid
      WHERE ( 
        (dd.datasetid IS NULL) OR 
        ( td.last_seen < dd.max_last_seen and dd.datasetid = td.datasetid)
      ) """
  deleted_datasets = PostgresStuff.commitQry(conn, deleted_datasets_qry)
  return deleted_datasets

def generate_deleted_report(conn):
  qry = SELECT 


def main():
  curr_full_path = FileUtils.getCurrentDirFullPath()
  config_fn = 'portal_activity_job_config.yaml'
  cI =  ConfigUtils(curr_full_path+ "/configs/" , config_fn)
  configItems = cI.getConfigs()
  configItems['config_dir'] = curr_full_path+ "/configs/"
  db_ini = configItems['config_dir'] + configItems['database_config']
  db_config = PostgresStuff.load_config(filename=db_ini)
  conn_alq, meta_alq =PostgresStuff.connect_alq(db_config)
  conn = PostgresStuff.connect()
  db_tbl = configItems['db_table']
  insert_deleted = updateDeletedDatasets(conn, configItems['deleted_time_iterval'])


if __name__ == "__main__":
    main()