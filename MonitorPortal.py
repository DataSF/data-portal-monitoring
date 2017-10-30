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
  	def generateReport(curr_full_path, output_dir, report_fn, df_shts):
  		wkbk_fn = WkbkUtilsWrite.wkbk_name(os.path.join( curr_full_path, output_dir, report_fn))
  		return PandasToExcel.writeWkBks(wkbk_fn, df_shts)



  		