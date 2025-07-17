

import os
import fastf1
import pandas as pd
from sqlalchemy import create_engine
from prefect import flow, task
from config import DB_URL, FASTF1_CACHE
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(DB_URL)

@task
def fetch_laps(
    year: int = 2025,
    gp_name: str = "Australian Grand Prix",
    session_name: str = "FP1"
) -> pd.DataFrame:
    # ensure cache folder exists
    os.makedirs(FASTF1_CACHE, exist_ok=True)
    fastf1.Cache.enable_cache(FASTF1_CACHE)
    session = fastf1.get_session(year, gp_name, session_name)
    
    # 4) *explicitly* load laps + telemetry + weather
    session.load(laps=True, telemetry=True, weather=True)
    
    # #To print column names in order to fecth required columnn names 
    # laps_df = session.laps
    # print("Available columns:", laps_df.columns.tolist())
    
    
    # 5) now session.laps is populated
    df = (
        session.laps
               [['Driver','LapNumber','LapTime','LapStartDate']]
               .dropna()
               .rename(columns={
                   'Driver':'driver',
                   'LapNumber':'lap_num',
                   'LapTime':'lap_time',
                   'LapStartDate':'recorded_at'
               })
    )
    df['lap_time'] = df['lap_time'].dt.total_seconds()
    return df

@task
def write_db(df):
    df['session'] = 'FP1'
    print(df.dtypes)
    # print(df['recorded_at'].head())
    df.to_sql('lap_times', engine, if_exists='append', index=False)


@flow(name="lap-collector")
def lap_collector_flow():
    df = fetch_laps()
    write_db(df)

if __name__ == "__main__":
    lap_collector_flow()

