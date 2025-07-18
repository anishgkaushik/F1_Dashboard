Setup Summary: PostgreSQL 17 & TimescaleDB (Homebrew, macOS)
1. Install PostgreSQL 17

brew install postgresql@17
echo 'export PATH="$(brew --prefix postgresql@17)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
initdb --locale=C -E UTF8 "$(brew --prefix)/var/postgresql@17"
brew services start postgresql@17

2. Install TimescaleDB

brew tap timescale/tap
brew install --build-from-source timescale/tap/timescaledb

3. Link Libraries & Control Files

Symlink TimescaleDB .dylib files into Postgres’s $(pg_config --pkglibdir)

Copy or symlink .control and SQL files into $(brew --prefix)/share/postgresql@17/extension

4. Configure & Verify

Ensure shared_preload_libraries = 'timescaledb' in postgresql.conf

Restart: brew services restart postgresql@17

Verify:

SHOW shared_preload_libraries;
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
\dx

Done! PostgreSQL 17 with TimescaleDB is now up and running.

### 1. Run Database Migrations  
```bash
# make sure your DB exists
createdb f1_telemetry

# apply the schema (creates hypertable)
psql f1_telemetry < migrations/001_create_lap_times.sql
2. Spin Up the ETL Pipeline

# start Prefect’s orchestration server
prefect orion start

# register & deploy your flow (once)
prefect deployment build flows/collect_lap_times.py:flow \-n "Collect Lap Times" --apply

# run an agent to execute scheduled runs
prefect agent start --work-queue default
3. Launch the Dashboard

# in a separate terminal
python dashboards/app.py
Point your browser at http://127.0.0.1:8050 to view live lap-time charts.





###############---------one‐stop shell script--------##############
# 0) From your project root:
cd ~/Desktop/F1_Dashboard

# 1) Start Postgres/TimescaleDB
brew services start postgresql       # or postgresql@<version> if you installed a versioned formula

# 2) Create the database & enable TimescaleDB
psql postgres -c "CREATE DATABASE f1_telemetry;"
psql f1_telemetry -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"

# 3) Run your schema migration
psql f1_telemetry < migrations/001_create_lap_times.sql

# 4) Create & activate your Python venv
python3 -m venv .venv
source .venv/bin/activate

# 5) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6) (Optional) seed initial data by triggering one run locally
python -m flows.collect_lap_times

# 7) Start the Prefect local server & UI
prefect server start 

# 8) Point your worker at the API (in the same session)
export PREFECT_API_URL="http://127.0.0.1:4200/api"

# 9) Deploy your flow (register it)
prefect deploy flows/collect_lap_times.py:lap_collector_flow \
  --name "Collect Lap Times" \
  --work-queue default 

# 10) Bring up a worker to pick up scheduled runs
prefect worker start --work-queue default 

# 11) Kick off a manual run
prefect deployment run "collect_lap_times/Collect Lap Times"

# 12) Launch the Dash app
python dashboards/app.py
