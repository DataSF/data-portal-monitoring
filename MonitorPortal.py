# coding: utf-8
#!/usr/bin/env python


from PandasUtils import *
from Utils import *
from Emailer import *

class MonitorPortal:

  @staticmethod
  def generateReportSht(conn_alq, qry, sht_name):
    sht = {}
    sht['df'] = PostGresPandas.qryToDF(conn_alq, qry)
    sht['sht_name'] =  sht_name
    return sht

  @staticmethod
  def generateReportWkBk(configItems, activity, df_shts):

    return wkbk_fn 

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
    #em = Emailer(configItems)
    #em.sendEmails(subject_line, msg_body, fname_attachment=email_content['report_attachment_name'], fname_attachment_fullpath= email_content['report_attachment_fullpath'])
    return notification_datsetids


  @staticmethod
  def generateEmail(conn_alq, configItems, activity, df_sheets):
    email_content = MonitorPortal.generateEmailContent(configItems, activity, df_sheets)
    return MonitorPortal.generateEmailMsg(configItems, activity,  email_content)

  
if __name__ == "__main__":
    main()