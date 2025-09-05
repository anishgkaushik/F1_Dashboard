-- migrations/V007__recreate_lap_times_enriched_numeric_time.sql


CREATE TABLE IF NOT EXISTS lap_times_enriched (
  year                   INT        NOT NULL,
  gp                     TEXT       NOT NULL,
  session                TEXT       NOT NULL,

  "Time"                 DOUBLE PRECISION,  -- was TIMESTAMPTZ
  "Driver"               TEXT,
  "DriverNumber"         INT,
  "LapTime"              DOUBLE PRECISION,  -- was INTERVAL
  "LapNumber"            INT,
  "Stint"                INT,

  "PitOutTime"           DOUBLE PRECISION,  -- was TIMESTAMPTZ
  "PitInTime"            DOUBLE PRECISION,  -- was TIMESTAMPTZ

  "Sector1Time"          DOUBLE PRECISION,  -- was INTERVAL
  "Sector2Time"          DOUBLE PRECISION,
  "Sector3Time"          DOUBLE PRECISION,

  "Sector1SessionTime"   DOUBLE PRECISION,  -- was INTERVAL
  "Sector2SessionTime"   DOUBLE PRECISION,
  "Sector3SessionTime"   DOUBLE PRECISION,

  "SpeedI1"              INT,
  "SpeedI2"              INT,
  "SpeedFL"              INT,
  "SpeedST"              INT,

  "IsPersonalBest"       BOOLEAN,
  "Compound"             TEXT,
  "TyreLife"             INT,
  "FreshTyre"            BOOLEAN,
  "Team"                 TEXT,

  "LapStartTime"         DOUBLE PRECISION,  -- was TIMESTAMPTZ
  "LapStartDate"         DATE,

  "TrackStatus"          TEXT,
  "Position"             INT,
  "Deleted"              BOOLEAN,
  "DeletedReason"        TEXT,
  "FastF1Generated"      BOOLEAN,
  "IsAccurate"           BOOLEAN,

  PRIMARY KEY (year, gp, session, "Driver", "LapNumber")
);
