

# Quick Start :

- This repo uses timescaledb and python to monitor the San Francisco Open Data Portal
- Specifically, it monitors when datasets are created, deleted and updated
- When an create, update or update event occurs within a specified monitoring time period, an email alert is sent. 

To run this repo out of the box: 

1. clone the repository
2. Modify the  email_config.yaml and portal_activity_job_config.yaml file to reflect your situation. 
3. Then run `setup.sh`
	1. This script will build a custom docker image with airflow and the tools in this repo
	2. Docker compose will instantiate a airflow image with the monitoring jobs and a timescaledb database
	3. All your timescaledb data default into a docker volume, at ./postgres-data. You can change the location of this volume in the docker-compose.yaml file 

4. Go to http://localhost:8080/admin/ to see the airflow instance run the monitoring jobs


The article below provides a general overview on how to monitor an municipal open data portal. 
This repository contains tools to get Open Data Activity Metrics and send out related notifications around these events. 

## [How to Monitor Your Open Data Portal](https://docs.google.com/document/d/1BKHuxtOr0uZMlejgqnUZt-BoVaZ52VBDxXpdFXzLpTU/edit?usp=sharing)

Having monitoring data is a necessary condition for observability into the inner workings of your  open data portal. 
At DataSF, we strive to:
- Provide data that is usable, timely, and accessible
- Ensure that data on the open data portal is understood, documented and of high quality

Monitoring our open data portal helps us quantify how well we're achieving our high level goals. 
At an operational level, collecting and classifying data about our open data portal enables our program to do the following:
- Quickly investigate and get to the bottom of data availability and high level data quality issues
- Provide a basis to receive meaningful, automated alerts about potential problems 
- Minimize service degradation and disruption

It is cheap to collect monitoring data, but not having monitoring data can be expensive, in terms in of staff time, user trust, and program reputation. As much as it’s reasonably possible, open data programs should collect as much useful data about their open data portals as they can. And then combine that with a monitoring and alert plan to respond to events on the portal.

## Monitoring Metrics

A metric captures a value pertaining to an open data portal at a specific point in time. For instance, a metric could record the the number of records in a dataset, or when a dataset was last updated. Metrics are collected at regular intervals to monitor an open data portal over time.
There are three main categories of metrics that open data programs should collect about their open data portals: data portal activity metrics, data quality metrics, and event metrics

- **Open Data Activity Metrics**: top level metrics that indicate create, read, update, delete and permissioning activities to data on your open data portal. 
- **Data Quality Metrics**: high level measures that let you understand the overall quality of the data on your open data portal
- **Event Metrics**: discrete, infrequent occurrences that relate to our open data portal; these can be data infrastructure events or other one bugs/issues; these can be used to investigate issues across correlated systems and/or datasets.  

## Data Portal Activity Metrics

Data portal activity metrics indicate the top level health of your open data portal by measuring when various activities occur on the platform. 
It’s helpful to segment your data portal activity metrics into five sub-types:

- **Create Activities**: metrics that capture when something on the open data portal is created and the responsible party; this could include when datasets, fields, records, etc are created. These metrics can be used to quantify how old a dataset or field is. 
- **Read Activities**: metrics that capture how many times a dataset is queried, downloaded, or viewed on the the open data portal.
- **Update Activities**: metrics that capture when something on the open data portal is updated and the responsible party; this could include when datasets, fields, records, etc  are altered. These metrics can assess whether or not data on the portal is being refreshed in a timely manner. 
- **Delete Activities**: metrics that capture when something on the open data portal gets deleted and the responsible party; this could include when datasets, fields, records, etc are deleted or go missing
- **Permissioning Activities**: metrics that capture when an event relating permissions occurs; for instance, this metric could capture an owner of a dataset changing, publication status of a dataset, or quantify how many public datasets are on an open data portal. 

The metrics above are important for observability. They are broad measures that can help an open data program answer its most pressing questions about the health and performance of their open data portal: What data is currently available on the open data portal? When was it created? Are certain datasets on the portal being updated as expected? Do the appropriate users have access to data on the open data portal? If data is not available, when was it deleted?

## Data Quality and Profiling Metrics
Data quality metrics help you assess if the data on the your open data portal is fit to serve its purpose in a given context. 
- Monitoring data quality provides three important benefits:
- Assists in the discovery of anomalies within the data
- Surface issues or problems that users might run into when they start working with the data
- Help you assess and validate metadata

To come up with data quality metrics, you should focus on these aspects of data quality: 
- Correctness/Accuracy: does the data reflect valid values?
- Consistency: single version of truth or is it different depending on source/version?
- Completeness: is the data complete?

As you develop your data quality metrics, you should consider the different levels of granularity of your data. 
For instance, on DataSF’s open data portal, the majority of data is stored as datasets. Each dataset contains a number of fields/columns. As a result, we chose to analyze our data at the dataset level and the field level. 

Here are some examples of dataset level data quality metrics:
- total number of records, field count, duplicate count, percentage documented, global field count,

Here are some examples of field level data quality metrics:
- Null count, missing count, actual count, cardinality, completeness, distictness, uniqueness, is a primary key, min field len, max field length, mean, median, mode, range, sum, standard deviation, variance, 
mean absolute deviation, IQR, kurtosis, skewness

## Event Metrics
In addition to data portal activity and data quality metrics collected at regular intervals, we also need to capture discrete, infrequent occurrences that relate to our open data portal. These events capture what transpired, a timestamp, with any additional discretionary information.

Unlike a single metric data point that is only meaningful in context, an event should collect enough information to be meaningful on its own.  Events can be used to generate alerts or advisories, in situations where someone needs to be notified where critical work failed or where dramatic changes were made. Events can also be used to investigate issues across correlated systems and/or datasets.  

Some examples of events metrics for open data portals are:
- **Changes**: known changes to a dataset or set of datasets (For example, 311 changed the schema of its calls for service dataset)
- **Alerts**: known issues or problems with data quality of dataset, known times/days a dataset is down/unavailable, other infrequent events that explain the state of your open data portal
- **Data Infrastructure Events**: events that occur outside your open data portal but affect the overall activity on on your open data portal. For instance, an ETL server in your publishing system is down. This event doesn’t occur on your open data per se, but when the ETL server goes down, certain publishing jobs won’t run and thus, certain datasets won’t be updated on time

## How to Collect Good Metrics About your Open Data Portal
Remember, metrics about your open data portal are really just data points.  The data you collect about your open data portal should have the following four characteristics:

- **Well Understood**: If an issue on your open data portal arises, you don’t want to spend time figuring out what your data means. You and your team should be able to quickly determine how each metric was captured and what the metric means. It’s best to keep your metrics simple, with clear names, and use the concepts outlined above. 
- **Granular**: One goal of collecting metrics is to be able to reconstruct the state of your open data portal at a specific point in time. If you collect metrics too infrequently or average values over long periods of time, it will be very difficult to do this. You should collect metrics at a frequency that it won’t conceal problems; at the same time, you shouldn’t be collecting metrics so often that it becomes taxing or at a sampling interval that is  too short to contain meaningful data. 
- **Tagged by Scope**: you have different scopes on your open data portal: the open data portal as a whole, a dataset, a field/column within a dataset, a record within a dataset. You will want to  check the aggregate health of any one of these scopes or their combinations. 
- **Longed-Lived**: It’s important to think about how long you want to retain your monitoring data. If you discard the data too soon, or after a period of time that your monitoring system aggregates your metrics, you may lose important information about what happened in the past. Retaining your raw monitoring data for at least a year makes easier to figure out what’s normal; it’s not uncommon to have metrics that have monthly or seasonal variations.

## Using Monitoring Data for Alerts and Diagnostics

After collecting your monitoring data, you will probably use it as a trigger to send out automated alerts and notifications. 
You will need to think about how your monitoring data relates to different levels of alerting urgency. 

There are three levels of alerts:
- **Record**: something that gets recorded in the monitoring system in case it becomes useful later for analysis or investigation; it doesn’t automatically send out a notification
- **Notification**:  an automatically generated, moderately urgent alert that notifies someone in unobtrusive way, such as via email or a chabot  that he or she needs to investigate and potentially fix a problem. 
- **Page**: an urgent  alert sent to someone, regardless of whether they are at work or sleeping. Pages are designed to be invasive and immediately redirect the responders attention to investigate a problem or incident. 

## Setting Up Alerts
When you set up alerts, you should ask yourself three questions to determine the alert’s level of urgency and how it should be handled. 

- *Is this an actual issue?*: How serious is this issue? Obvious as it may seem, it’s important to only issue alerts for real issues. Overly using notifications can contribute to alert fatigue and may cause your team to ignore more serious issues.  

- *Does the issue require attention?*: If there is an actual issue and requires attention, it should generate a notification that notifies that someone who can investigate the problem. A notification should be sent via email, chatbot or other written means to help recipients prioritize their response.

- *How urgent is the incident?*: All emergencies are issues but not all issues are emergencies. When creating alerts, consider severity of a potential issue and what the acceptable response time would be resolve the issue. 

## Open Data Diagnostics
It’s important to note that your motoring metrics will capture a symptom of an issue or problem on your open data portal. A manifestation of an issue could have one or many different causes. For example, unbeknownst to your program staff, four, frequently used public datasets have been mysteriously deleted off your open data portal in past 24 hours. Possible causes of the datasets disappearing are your open vendor provider, the department who provided the data, an unauthorized user, etc. Once your monitoring system has notified symptom that requires attention, you and your team will need to diagnose the root cause using the monitoring data that you've collected.

Earlier we outlined three types of monitoring data that can help you investigate the root causes of problems on your open data portal:

- *Open Data Activity Metrics*: top level metrics that indicate create, read, update, delete and permissioning activities. 
- *Data Quality Metrics*: high level measures that let you understand if the data on your open data portal is fit to serve its purpose in a given context
- *Event Metrics*: discrete, infrequent occurrences that relate to our open data portal

On the whole, open data activity metrics will surface the most serious symptoms of something awry and should therefore generate the most alerts. However, the other metrics are invaluable for investigating the causes of those symptoms. 
Thinking about how data portal activities relate to data quality and various events can help you efficiently get to the root of any issues that surface. Understanding the hierarchies between the activity on your open data portal and data quality helps you build a mental model of how various components of your open data portal interact so that you can quickly focus in on the key diagnostic metrics for any incident. When you or your team receives a notification alerting you problem, the following framework below can helpful in systematically investigating an issue.

1. **Start with data activity metrics**
Start by asking yourself, "What's the problem? How would I characterize it?" At the outset, you need to clearly describe the problem before diving deeper. Next look at the high level open data activity metrics. These will often disclose the source of  problem, or at least steer your investigation in a particular direction. For instance, a user reports that police calls for service dataset, there's no crime data for the last 2 weeks. Looking at your data activity metrics, you would quickly see that the dataset hadn't been updated in two weeks. You would also see that that owner of the dataset changed three weeks ago, helping you further hone in on the cause of the problem. 
2. **Dive into data quality metrics**
If you haven't found the cause of the issue by inspecting your data activity metrics, examine the your data quality metrics.  You should be able to quickly find an peruse these metrics to look for outliers and anomalies, incomplete data or data that inaccurately describes the real world/doesn't make sense
3. **Did something change?**
Next, consider events or other alerts that could be correlated with your issue. If an event was registered slightly before the problems started, investigate whether or not it’s connected to the problem. 
4. **Fix it (and improve it for next time!)**
 After you’ve found the root cause of the problem, fix it. Although the investigation is complete, it’s usually worth taking some time to think about how to change your system, publishing or business process to avoid similar problems in the future. If you found that you lacked the monitoring data you needed to quickly diagnose the problem, consider implementing additional monitoring metrics to help future responders. 

## Monitoring Dashboards
Setting up monitoring dashboards in advance of problem can greatly speed up your investigation. Monitoring dashboards can help you observe the current and recent state of your open data portal and make potential problems more visible than just looking at raw data. You may want to set up a dashboard for your data portal activity metrics, one dashboard that displays your data quality metrics. When setting up your dashboards, consider the various levels granularity that exist on your open data portal, and how they relate to one another, so that you'll be able to roll your monitoring metrics up or down easily.

## Conclusions
Collect as many data portal activity, data quality and event metrics as you can. Observability of your open data portal demands comprehensive metrics. 

- Make sure to collect metrics with sufficient granularity so that you can reconstruct the state of your open data portal at specific point in time. 
- To maximize the value of your monitoring data, tag metrics and events with several scopes and retain them for at least 12 months. 
- You will use your monitoring data as trigger to send out automated alerts.

There are three levels of alerts: record, notify and page, that indicate the alert’s severity

- Different mediums are appropriate for different levels of alert. For instance, an email is an appropriate level for a notification, while a phone call is appropriate for a page.
- Using a standardized monitoring framework will empower you your team to investigate problems on your open data portal more systematically. 
- Alerts will notify you with symptoms of a problem; you and your team need to figure out the cause

Set up dashboards ahead of time that displays all of your key data portal activity and data quality metrics
Investigate causes of problems by first examining data portal activity metrics, and then review data quality metrics and any associated events. 

At DataSF, we have just begun the process of setting up a way to comprehensive monitoring program of our open data portal. We would love to hear about your experiences monitoring your open data portal. If you have comments, questions, additions, corrections or complaints, let us know on twitter! We’d love to hear from you. 

## References
- Alexis Lê-Quôc, (2015, June 30). Monitoring 101: Collecting the right data. Retrieved from https://www.datadoghq.com/blog/monitoring-101-collecting-data
- Alexis Lê-Quôc, (2015, July 16). Monitoring 101: Investigating Performance Issues. Retrieved from https://www.datadoghq.com/blog/monitoring-101-investigation/
- Alexis Lê-Quôc, (2015, July 16). Monitoring 101: Alerting on What Matters. Retrieved from https://www.datadoghq.com/blog/monitoring-101-alerting/

## Appendix- Additional Resources About Systems Monitoring and Alerting
- Systems Monitoring
  - Brendan Gregg. The Utilization Saturation and Errors (USE) Method http://www.brendangregg.com/usemethod.html
- Alerts and Notifications
  - Rob Ewaschuk. My Philosophy on Alerting https://docs.google.com/document/d/199PqyG3UsyXlwieHaqbGiWVa8eMWi8zzAn0YfcApr8Q


