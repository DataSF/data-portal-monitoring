# coding: utf-8
#!/usr/bin/env python

import pandas as pd
import json
from pandas.io.json import json_normalize
import unicodedata as ucd
from openpyxl import Workbook

class PandasUtils:

  @staticmethod
  def getWkbk(fn):
    wkbk = pd.ExcelFile(fn)
    return wkbk


  @staticmethod
  def removeCols(df, list_of_cols_to_remove):
    '''removes cols inplace'''
    df_col = list(df.columns)
    #check to make sure that column exists in the dataframe
    list_of_cols_to_remove = [col for col in list_of_cols_to_remove if col in df_col]
    return df.drop(list_of_cols_to_remove, axis=1)
    #return df.drop(df[list_of_cols_to_remove],inplace=True,axis=1)

  @staticmethod
  def castDateFieldsAsString(df, list_of_date_cols, dt_format):
    for col in list_of_date_cols:
      df[col] =  df[col].dt.strftime(dt_format)
    return df

  @staticmethod
  def loadCsv(fullpath):
    df = None
    try:
      df = pd.read_csv(fullpath)
    except Exception as e:
      print (str(e))
    return df

  @staticmethod
  def fillNaWithBlank(df):
    return df.fillna("")

  @staticmethod
  def makeDfFromJson(json_obj):
    df = json_normalize(json_obj)
    return df

  @staticmethod
  def convertDfToDictrows(df):
    return df.to_dict(orient='records')

  @staticmethod
  def mapFieldNames(df, field_mapping_dict):
    return df.rename(columns=field_mapping_dict)

  @staticmethod
  def renameCols(df, colMappingDict):
    df = df.rename(columns=colMappingDict)
    return df

  @staticmethod
  def groupbyCountStar(df, group_by_list):
    return df.groupby(group_by_list).size().reset_index(name='count')

  @staticmethod
  def colToLower(df, field_name):
    '''strips off white space and converts the col to lower'''
    df[field_name] = df[field_name].astype(str)
    df[field_name] = df[field_name].str.lower()
    df[field_name] = df[field_name].map(str.strip)
    return df

  @staticmethod
  def makeLookupDictOnTwo(df, key_col, val_col):
      return dict(zip(df[key_col], df[val_col]))


  @staticmethod
  def dfToHTMLTable(df, headers):
    def html_tags(tag, item):
      backtag = "</" + tag[1:] 
      return tag + item +backtag 
    df_list = PandasUtils.convertDfToDictrows(df)
    headers = headers.split(', ')
    header = [ html_tags('<th>', vals) for vals in headers ]
    table_rows = ['<table style="border-collapse:collapse">', '<tr style="border: 1px solid black;">'] +  header  + ['</tr>']
    if (not(df_list is None)):
      print (len(df_list))
      for item in df_list:
        item_vals = []
        for col in headers:
          item_vals.append(item[col])
        row = [ html_tags('<td style="border: 1px solid black; padding:2px">', vals) for vals in  item_vals]
        row = ['<tr>'] + row
        row.append('</tr>')
        table_rows = table_rows + row
      table_rows.append("</table>")
    return " ".join(table_rows)

class PostGresPandas:

  @staticmethod
  def qryToDF (conn_alq, qry ):
    '''takes a qry and returns a dataset'''
    df = pd.read_sql_query(qry, con=conn_alq)
    return df

class PandasToExcel:


  @staticmethod
  def writeWkBks(wkbk_fn, df_shts, showIndex=False):
    '''takes a list of dict items and turns them into sheets
      dict items are structured like this:
      {'shtName': 'mysheet', 'df': df}
    '''
    writer = pd.ExcelWriter(wkbk_fn,  engine='xlsxwriter',  options={'remove_timezone': True})
    workbook = writer.book
    cell_format = workbook.add_format({'bold': True, 'font_size': '35', 'font_name': 'Arial'})
    #shtFormat = workbook.add_format({'bold': True, 'font_color': 'red'})
    for sheetItem in  df_shts:
      sheetItem['df'].to_excel( writer,  index=showIndex,  sheet_name=sheetItem['sht_name'], )
      worksheet = writer.sheets[sheetItem['sht_name'] ] # pull worksheet object
      worksheet.set_zoom(90)
      for idx, col in enumerate(sheetItem['df']):  # loop through all columns
        series = sheetItem['df'][col]
        try:
          max_len = max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
          if(max_len == 0 or math.isnan(max_len)):
            len(str(series.name))
        except:
          max_len = 15
        worksheet.set_column(idx, idx, max_len)  # set column width
      worksheet.set_row(0,None, cell_format)
    writer.save()
    return True


if __name__ == "__main__":
    main()