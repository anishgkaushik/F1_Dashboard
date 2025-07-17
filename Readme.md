Setup Summary: PostgreSQL 17 & TimescaleDB (Homebrew, macOS)

1. Cleanup

Stop & uninstall any postgresql@*, postgresql, timescaledb, timescaledb-tools

Remove Homebrew taps, plists, data directories, and configs

2. Install PostgreSQL 17

brew install postgresql@17
echo 'export PATH="$(brew --prefix postgresql@17)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
initdb --locale=C -E UTF8 "$(brew --prefix)/var/postgresql@17"
brew services start postgresql@17

3. Install TimescaleDB

brew tap timescale/tap
brew install --build-from-source timescale/tap/timescaledb

4. Link Libraries & Control Files

Symlink TimescaleDB .dylib files into Postgres’s $(pg_config --pkglibdir)

Copy or symlink .control and SQL files into $(brew --prefix)/share/postgresql@17/extension

5. Configure & Verify

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
prefect deployment build flows/collect_lap_times.py:flow \
  -n "Collect Lap Times" --apply

# run an agent to execute scheduled runs
prefect agent start --work-queue default
3. Launch the Dashboard

# in a separate terminal
python dashboards/app.py
Point your browser at http://127.0.0.1:8050 to view live lap-time charts.