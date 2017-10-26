

import requests

def parseResults(dataset):
    fields = []
    fields.append(dataset["view"]['id'])
    fields.append(dataset["view"]['name'])
    fields.append(dataset["view"]['createdAt'])
    fields.append(dataset["view"]['rowsUpdatedAt'])
    print dataset['view']["metadata"]["custom_fields"]
    fields.append(dataset['view']["metadata"]["custom_fields"]["Department Metrics"]["Publishing Department"])
    fields.append(dataset['view']["metadata"]["custom_fields"]["Publishing Details"]["Publishing frequency"])
    return fields

def main():
  print "here"
  r = requests.get('https://data.sfgov.org/api/search/views.json')
  print "here"
  datasets = r.json()
  csv_data = []
  datasets = datasets['results']
  for dataset in datasets:
    print dataset
    fields = parseResults(dataset)
    print fields



if __name__ == "__main__":
    main()
