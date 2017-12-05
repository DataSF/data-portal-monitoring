
# coding: utf-8
#!/usr/bin/env python
from Utils import *
from ConfigUtils import *
from PostgresStuff import *
from PandasUtils import *
from MonitorPortal import *


def rotateActivityData(conn):
  #drop the chunks on the hyper table that are older than two weeks
  rotate_qry = """
      SELECT drop_chunks(interval '2 weeks', 'portal_activity');
    """ 
  dropped_chunks = PostgresStuff.commitQry(conn, rotate_qry)
  return dropped_chunks


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
  rotate_items = rotateActivityData(conn)
  activity = "rotate_portal_activity"
  subject_line = configItems['activity'][activity]['email_msg']['subject_line']
  msg_body = configItems['email_msg_template']['header'] + configItems['activity'][activity]['email_msg']['msg']
  msg_body = msg_body +  configItems['email_msg_template']['footer']
  em = Emailer(configItems)
  em.sendEmails(subject_line, msg_body.encode('utf-8').strip())


  


if __name__ == "__main__":
    main()