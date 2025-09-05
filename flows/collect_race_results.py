

import os
from dotenv import load_dotenv

# 1) Load environment variables so config.py picks them up
load_dotenv()

import fastf1
from fastf1 import Cache
import pandas as pd
from sqlalchemy import create_engine
from prefect import flow, task
from config import DB_URL, FASTF1_CACHE
from fastf1._api import SessionNotAvailableError
from fastf1.core   import DataNotLoadedError

# 2) Initialize DB engine
engine = create_engine(DB_URL)

@task
def extract_results(year: int, gp_name: str, session_type: str) -> pd.DataFrame:
    # Extracts full qualifying lap data or race results for a given GP session.
    
    # 3) Ensure cache folder exists and enable FastF1 caching
    yield_dir = FASTF1_CACHE if 'FASTF1_CACHE' in globals() else os.getenv('FASTF1_CACHE')
    print(f"[Debug] Using FASTF1_CACHE: {yield_dir}")
    os.makedirs(FASTF1_CACHE, exist_ok=True)
    fastf1.Cache.enable_cache(FASTF1_CACHE)

    # Fetch session and load all data
    session = fastf1.get_session(year, gp_name, session_type)
    try:
        # Gets only GP's till date 
        # Parse event dates
        # schedule['EventDate'] = pd.to_datetime(schedule['Date'])
        # # Keep only events that have already occurred
        # schedule = schedule[schedule['EventDate'] <= pd.Timestamp.now()]
        # # Filter to actual Grands Prix
        # schedule = schedule[schedule['EventName'].str.contains('Grand Prix')]



        # session.load(laps = True, telemetry = True, weather = True)  # loads laps, telemetry, weather
        session.load()

        if session_type.lower() == 'Qualifying':
            # Use the complete laps DataFrame
            laps = session.laps.copy()
            df = laps[['Driver','Number','LapNumber','LapTime','LapStartDate','Team','Grid']].copy()
            df.rename(columns={
                'Driver':'driver',
                'Number':'drivernumber',
                'LapNumber':'lap_num',
                'LapTime':'lap_time',
                'LapStartDate':'recorded_at',
                'Team':'team_name',
                'Grid':'grid_pos'
            }, inplace=True)
            # Convert lap_time to numeric seconds
            df['lap_time'] = df['lap_time'].dt.total_seconds()
            df['session'] = f"{year}-{gp_name}-qualifying"
            df['result_type'] = 'qualifying'
        else:
            # Race final positions
            records = session.results
            df_src = pd.DataFrame(records)
            df = pd.DataFrame({
                'drivernumber': df_src['DriverNumber'],
                'session': f"{year}-{gp_name}-race",
                'driver': df_src['FullName'],
                'result_pos': df_src['Position'],
                'points': df_src['Points'],
                'team_name': df_src.get('TeamName'),
                'grid_pos': df_src.get('GridPosition'),
                'gap': df_src['Time'],

            })
            # df['result_type'] = 'Status'
            df['recorded_at'] = pd.Timestamp.now()

        return df
    except(SessionNotAvailableError, DataNotLoadedError) as e:
        print(f"[Warning] Data for {gp_name} {session_type} not available: {e}")
        # return pd.DataFrame(columns=[])
        

@task
def load_results(df: pd.DataFrame):
    # if df.empty:
    #     print(f"[Info] Skipping load: got empty DataFrame.")
    #     return
    # print(f"[Info] Writing {len(df)} rows to `results`")

    # Loads the normalized DataFrame into the Postgres 'results' table.
    df.to_sql('results', con=engine, if_exists='append', index=False)

@flow(name="results_collector_flow")
def results_collector_flow(year: int = 2025):

    # Prefect flow to collect qualifying and race results for the full season.

    schedule = fastf1.get_event_schedule(year)
    for _, event in schedule.iterrows():
        gp_name = event['EventName']
        for session_type in ['Qualifying','Race']:
            df = extract_results(year, gp_name, session_type)
            load_results(df)

if __name__ == '__main__':
    results_collector_flow()