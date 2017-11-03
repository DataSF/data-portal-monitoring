
-- We start by creating a regular SQL table

DROP TABLE IF EXISTS portal_activity;
CREATE TABLE portal_activity (
  time        TIMESTAMPTZ       NOT NULL,
  datasetid    varchar(250),
  name varchar(250),
  created_at timestamp,
  updated_at timestamp,
  pub_dept varchar(250), 
  pub_freq varchar(250),
  pub_health varchar(100),
  days_last_updt varchar(100)
);

-- This creates a hypertable that is partitioned by time
--   using the values in the `time` column.

SELECT create_hypertable('portal_activity', 'time');
-- see this for more info: http://docs.timescale.com/latest/api/api-timescaledb#create_hypertable-best-practices


DROP TABLE IF EXISTS deleted_datasets;
CREATE TABLE deleted_datasets(
	time        TIMESTAMPTZ       NOT NULL,
	datasetid    varchar(250),
	name 		varchar(250),
	last_seen  TIMESTAMPTZ NOT NULL,
	pub_dept   varchar(250), 
 	pub_freq varchar(250),
 	created_at timestamp, 
 	notification boolean
);

SELECT create_hypertable('deleted_datasets', 'time');
#ALTER TABLE deleted_datasets ALTER last_seen TYPE timestamptz USING last_seen AT TIME ZONE '';


DROP TABLE IF EXISTS created_datasets;
CREATE TABLE created_datasets(
	time        TIMESTAMPTZ       NOT NULL,
	datasetid    varchar(250),
	name 		varchar(250),
	first_seen  TIMESTAMPTZ       NOT NULL,
    created_at timestamp, 
	pub_dept   varchar(250), 
 	pub_freq varchar(250),
 	deleted_last_seen TIMESTAMPTZ , 
    time_btw_deleted_and_first_seen INTERVAL , 
 	notification boolean
);
SELECT create_hypertable('created_datasets', 'time');



CREATE TABLE stale_delayed_datasets(
	time        TIMESTAMPTZ       NOT NULL,
	datasetid    varchar(250),
	name 		varchar(250),
	last_updated  TIMESTAMPTZ       NOT NULL,
	pub_dept   varchar(250), 
 	pub_freq varchar(250),
  	pub_health varchar(100),
  	days_last_updt varchar(100)
 	notification boolean
);
SELECT create_hypertable('stale_delayed_datasets', 'time');

