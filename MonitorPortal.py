# coding: utf-8
#!/usr/bin/env python


from PandasUtils import *
from Utils import *
from Emailer import *
from datetime import datetime
from PostgresStuff import *
from datetime import datetime, timedelta
class MonitorPortal:

  @staticmethod
  def generateReportSht(conn_alq, qry, sht_name):
    sht = {}
    sht['df'] = PostGresPandas.qryToDF(conn_alq, qry)
    sht['sht_name'] =  sht_name
    return sht

  @staticmethod
  def generateActivityReport(conn_alq, configItems, activity):
    qry = '''
        SELECT time, datasetid,  name, %s, pub_dept, pub_freq, created_at
        FROM %s
        WHERE (notification is NULL) 
      ''' % (configItems['activity'][activity]['timestamp_report_notification_col'], configItems['activity'][activity]['database_table'])
    sht = MonitorPortal.generateReportSht(conn_alq, qry, configItems['activity'][activity]['report_fn'])
    if len(sht['df']) == 0:
      return False
    print sht['df']
    cols = ['time', configItems['activity'][activity]['timestamp_report_notification_col'], 'created_at']
    sht['df'] = PandasUtils.castDateFieldsAsString( sht['df'], cols, configItems['activity'][activity]['dt_format'])
    return [sht]




  @staticmethod
  def generateEmailContent(configItems, activity, df_shts):
    email_content = {}
    email_content['report_attachment_fullpath']  =  WkbkUtilsWrite.wkbk_name(os.path.join( configItems['curr_full_path'], configItems['report_output_dir'], configItems['activity'][activity]['report_fn']))
    wrote_wkbk =  PandasToExcel.writeWkBks(email_content['report_attachment_fullpath'], df_shts)
    email_content['report_attachment_name'] = None
    email_content['number_of_actions'] = 0 
    if wrote_wkbk == 1:
      fn = email_content['report_attachment_fullpath'].split("/")
      email_content['report_attachment_name'] = fn[-1]
    else:
      email_content['report_attachment_fullpath'] = None
    email_content_shts = []
    for sht in df_shts:
      email_content_sht = {}
      email_content_sht['datasetids'] = MonitorPortal.getDatasetIdsForNotification(sht['df'], configItems['activity'][activity]['timestamp_report_notification_col'])
      tbl_report_html = PandasUtils.dfToHTMLTable(sht['df'])
      email_content_sht['report_html']  = tbl_report_html
      email_content_shts.append(email_content_sht)
      email_content['number_of_actions'] += len(sht['df'])
    email_content['content'] = email_content_shts
    return email_content

  @staticmethod
  def getDatasetIdsForNotification(df, timestamp_col):
    return PandasUtils.convertDfToDictrows(df[['datasetid',  timestamp_col]])


  @staticmethod
  def generateEmailMsg(configItems, activity,  email_content):
    notification_datsetids = []
    msg_body = configItems['email_msg_template']['header'] + configItems['activity'][activity]['email_msg']['msg_header']
    attachment_list = []
    for content in  email_content['content']:
      msg_body = msg_body + "<p>" + content['report_html'] + "</p>"
      notification_datsetids = notification_datsetids + content['datasetids']

    subject_line = configItems['activity'][activity]['email_msg']['subject_line'] + ": " + str(email_content['number_of_actions']) + " " + configItems['activity'][activity]['email_msg']['subject_line_action']
    msg_body = msg_body +  configItems['email_msg_template']['footer']
    em = Emailer(configItems)
    em.sendEmails(subject_line, msg_body.encode('utf-8').strip(), fname_attachment=email_content['report_attachment_name'], fname_attachment_fullpath= email_content['report_attachment_fullpath'])
    return notification_datsetids


  @staticmethod
  def generateEmail(conn_alq, configItems, activity, df_sheets):
    email_content = MonitorPortal.generateEmailContent(configItems, activity, df_sheets)
    return MonitorPortal.generateEmailMsg(configItems, activity,  email_content)

  @staticmethod
  def updateNotifiedDatasetIds(conn, configItems, activity, datasetids):
    updt_cnt = 0
    time_analysis_col =  configItems['activity'][activity]['timestamp_report_notification_col'] 
    for dataset in datasetids:
      seen =  dataset[time_analysis_col].strip("\\")
      seen_obj = datetime.strptime(seen, configItems['activity'][activity]['dt_format'][1:])
      seen_obj =  seen_obj - timedelta(hours=configItems['time_zone_difference'])
      seen_str =  seen_obj.strftime(configItems['activity'][activity]['dt_format'])
      qry = """  
        UPDATE  %s 
        SET notification = 't'
        WHERE datasetid = '%s' 
        and %s = '%s' """  % (configItems['activity'][activity]['database_table'], dataset['datasetid'],  time_analysis_col,  seen_str[1:] )
      updated = PostgresStuff.update_records(conn, qry)
      updt_cnt += updated
    return updt_cnt



if __name__ == "__main__":
    main()