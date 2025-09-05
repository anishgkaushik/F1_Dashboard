# flows/collect_lap_times_enriched.py

import os
from dotenv import load_dotenv
import fastf1
import pandas as pd
from sqlalchemy import create_engine
from prefect import task, flow
from config import DB_URL, FASTF1_CACHE


# 1) load your .env so DATABASE_URL is available
load_dotenv()
engine = create_engine(DB_URL)

# ensure cache folder exists
os.makedirs(FASTF1_CACHE, exist_ok=True)
fastf1.Cache.enable_cache(FASTF1_CACHE)


@task
def fetch_calendar(year: int) -> list[str]:
    """
    Returns a list of Grand Prix names for the full season.
    """
    # This returns a pandas DataFrame with one row per session;
    # we take the unique EventName values (GP names).
    schedule = fastf1.get_event_schedule(year)
    return schedule["EventName"].unique().tolist()


@task
def fetch_laps(year: int, gp_name: str) -> pd.DataFrame:
    """
    Fetch FP1–Race laps for a single GP, flatten all columns,
    and add context columns.
    """
    dfs = []
    for ses in ("FP1", "FP2", "FP3", "Qualifying", "Race"):
        s = fastf1.get_session(year, gp_name, ses)
        s.load(laps=True)
        df = s.laps.copy()
        df["year"] = year
        df["gp"] = gp_name
        df["session"] = ses
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


from datetime import timedelta
import pandas as pd

@task
def write_db(df: pd.DataFrame):
    # 1) Convert pandas timedelta64 columns to floats
    for col in df.select_dtypes(include=["timedelta64[ns]"]).columns:
        df[col] = df[col].dt.total_seconds()

    # 2) Convert Python timedelta objects to floats
    for col in df.columns:
        if df[col].dtype == object and df[col].map(lambda x: isinstance(x, timedelta)).any():
            df[col] = df[col].map(lambda x: x.total_seconds() if pd.notnull(x) else None)

    # 3) Convert any remaining object columns (e.g. fastf1 objects) to strings
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)

    # 4) Debug: check final dtypes
    print("→ Final dtypes before write:")
    print(df.dtypes)

    # 5) Write in chunks of 500 rows without method="multi"
    df.to_sql(
        "lap_times_enriched",
        engine,
        if_exists="append",
        index=False,
        chunksize=500
    )
    print(f"→ Wrote {len(df)} rows in batches of 500")




@flow(name="lap-collector")
def lap_collector_flow(year: int = 2024):
    # 1) get the full list of GPs for the season
    gp_list = fetch_calendar(year)
    print("Completed task")

    # 2) for each GP, fetch laps and write to DB
    for gp in gp_list:
        laps_df = fetch_laps(year, gp)
        write_db(laps_df)


if __name__ == "__main__":
    lap_collector_flow()
