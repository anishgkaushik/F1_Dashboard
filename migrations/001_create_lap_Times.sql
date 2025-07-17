

CREATE DATABASE IF NOT EXISTS f1_telemetry;


CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;


CREATE TABLE IF NOT EXISTS lap_times (
  session   TEXT,
  driver    TEXT,
  lap_num   INTEGER,
  lap_time  DOUBLE PRECISION,
  recorded_at TIMESTAMPTZ
);

-- create the hypertable (no named if_not_exists)
SELECT create_hypertable('lap_times', 'recorded_at');
