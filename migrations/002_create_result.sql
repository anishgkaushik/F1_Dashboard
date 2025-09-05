
# Creation of race relust tables
 
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

CREATE TABLE IF NOT EXISTS results (
    DriverNumber INT not NULL,
    session TEXT NOT NULL,
    driver TEXT NOT NULL,
    result_pos INTEGER NOT NULL,
    gap INTERVAL,
    points NUMERIC,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    team_name TEXT,
    grid_pos INTEGER,
    PRIMARY KEY (session, driver, result_pos)
)