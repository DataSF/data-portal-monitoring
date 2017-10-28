
# coding: utf-8
#!/usr/bin/env python

def getDeletedDatasets(conn)
	deleted_datasets = '''

		DROP TABLE if exists tmp_deleted;

		CREATE TABLE tmp_deleted AS 
			
 			SELECT a.datasetid, last_seen
 			FROM  
 			(	
  				SELECT datasetid as datasetid, last(time, time) as last_seen
  				FROM portal_activity
  				WHERE time < NOW() - interval '80 minutes'
  				GROUP BY datasetid
  			) a 
  			LEFT JOIN 
  			(
  				SELECT datasetid, last(time, time)
  				FROM portal_activity
  				WHERE time > NOW() - interval '80 minutes'
  				GROUP BY datasetid
  			) b
  			ON a.datasetid = b.datasetid
  			WHERE b.datasetid is NULL;
  	'''

def main():
	curr_full_path = FileUtils.getCurrentDirFullPath()
  	config_fn = 'portal_activity_job_config.yaml'
  	cI =  ConfigUtils(curr_full_path+ "/configs/" ,config_fn)
 	configItems = cI.getConfigs()
  	configItems['config_dir'] = curr_full_path+ "/configs/"
  	db_ini = configItems['config_dir'] + configItems['database_config']
  	db_config = PostgresStuff.load_config(filename=db_ini)
  	total_inserted_rows = 0
  	conn_alq, meta_alq =PostgresStuff.connect_alq(db_config)
  	conn = PostgresStuff.connect()
  	db_tbl = configItems['db_table']
if __name__ == "__main__":
    main()