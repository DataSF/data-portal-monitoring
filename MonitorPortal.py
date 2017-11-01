# coding: utf-8
#!/usr/bin/env python


from PandasUtils import *
from Utils import *

class MonitorPortal:

  @staticmethod
  def generateReportSht(conn_alq, qry, sht_name):
    sht = {}
    sht['df'] = PostGresPandas.qryToDF(conn_alq, qry)
    sht['sht_name'] = 'Deleted Datasets'
    return sht

  @staticmethod
  def generateReportWkBk(curr_full_path, output_dir, report_fn, df_shts):
    wkbk_fn = WkbkUtilsWrite.wkbk_name(os.path.join( curr_full_path, output_dir, report_fn))
    wrote_wkbk = PandasToExcel.writeWkBks(wkbk_fn, df_shts)
    return wkbk_fn 

  @staticmethod
  def generateEmailContent(df_shts, configItems, report_fn):
    email_content_shts = []
    for sht in df_shts:
      email_content_sht = {}
      tbl_report_html = PandasUtils.dfToHTMLTable(sht['df'])
      email_content_sht['report_html']  = tbl_report_html
      email_content_sht['count'] = len(sht['df'])
      email_content_sht['report'] = report = MonitorPortal.generateReportWkBk( configItems['curr_full_path'], configItems['report_output_dir'], configItems[report_fn], [sht])
      email_content_shts.append(email_content_sht)
    return email_content_shts





if __name__ == "__main__":
    main()