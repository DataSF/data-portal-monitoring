

import requests
from Utils import *

def getDataFromWeb():
  r = requests.get('https://data.sfgov.org/api/search/views.json')
  datasets = r.json()
  return datasets['results']


def calculatePublishingHealth(dtFormat, pubFreq, monitoringTime, dayslastUpdt):
  if (monitoringTime is None) or (dayslastUpdt is None): 
    return "Unknown"
  dayslastUpdt = DateUtils.days_between(dayslastUpdt, dtFormat, monitoringTime, dtFormat)
  healthThresholds = {
    'Streaming': [2,4],
    'Daily' : [2,4],
    'Weekly': [7,21],
    'Monthly': [32, 90],
    'Bi-annually': [60, 180],
    'Annually': [365,500],
    'Quarterly': [90, 270]
  }
  if pubFreq is None:
    return 'Unknown'
  if pubFreq in healthThresholds.keys():
    timeIntervals = healthThresholds[pubFreq]
    if int(dayslastUpdt <= timeIntervals[0]):
      return 'On Time'
    elif ((int(dayslastUpdt) > timeIntervals[0]) and (int(dayslastUpdt) <= timeIntervals[1])):
      return 'Delayed'
    elif (int(dayslastUpdt) > timeIntervals[1]):
        return 'Stale'
  return 'On Time'


d
def parseResults(dataset):
    headers = ["time", "datasetid", "name", "created_at", "updated_at",  "pub_dept", "pub_freq", "pub_health"]
    dt_format=  '%Y-%m-%d %H:%M:%S'
    fields = []
    fields.append(DateUtils.get_current_timestamp_any_format(dt_format))
    fields.append(dataset["view"]['id'])
    fields.append(dataset["view"]['name'])
    fields.append(DateUtils.convertEpochToStrTime( dataset["view"]['createdAt'], dt_format))
    if 'rowsUpdatedAt' in dataset["view"].keys():
       fields.append(DateUtils.convertEpochToStrTime( dataset["view"]['rowsUpdatedAt'], dt_format))
    else:
      fields.append(None)
    if 'custom_fields' in dataset['view']["metadata"].keys():
      fields.append(dataset['view']["metadata"]["custom_fields"]["Department Metrics"]["Publishing Department"])
      if 'Publishing Details' in dataset['view']["metadata"]["custom_fields"].keys():
        if "Publishing frequency" in dataset['view']["metadata"]["custom_fields"]["Publishing Details"].keys():
          fields.append(dataset['view']["metadata"]["custom_fields"]["Publishing Details"]["Publishing frequency"])
        else:
          fields.append(None)
      else:
        fields.append(None)
    else:
      fields.append(None)
    fields.append()
    return fields

def main():
 
  csv_data = []
  datasets = getDataFromWeb()
  for dataset in datasets:
    fields = parseResults(dataset)
    print fields



if __name__ == "__main__":
    main()
