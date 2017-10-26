
-- We start by creating a regular SQL table
CREATE TABLE datasets (
  time        TIMESTAMPTZ       NOT NULL,
  datasetid    varchar(250),
  name varchar(250),
  created_at timestamp,
  updated_at timestamp,
  pub_freq varchar(250),
  pub_dept varchar(250)
);

-- This creates a hypertable that is partitioned by time
--   using the values in the `time` column.

SELECT create_hypertable('datasets', 'time');
-- see this for more info: http://docs.timescale.com/latest/api/api-timescaledb#create_hypertable-best-practices