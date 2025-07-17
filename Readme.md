
**README for PostgreSQL 17 + TimescaleDB Setup**

This document summarizes the successful steps taken to install, configure, and verify PostgreSQL 17 with TimescaleDB on macOS (Homebrew). Use this as a reference for future clean installs or troubleshooting.

---

## 1. Prerequisites

* macOS with Homebrew installed and updated:

  ```bash
  brew update
  ```
* No conflicting PostgreSQL or TimescaleDB installations (see Uninstall section).

---

## 2. Uninstall Any Previous Versions

To ensure a clean slate, remove older PostgreSQL versions and TimescaleDB:

```bash
# Stop and remove services
brew services stop postgresql@* postgresql 2>/dev/null || true
brew services stop --all 2>/dev/null || true

# Uninstall formulas
brew uninstall --force postgresql@* postgresql timescaledb timescaledb-tools --ignore-dependencies

# Remove taps and plists
brew untap timescale/tap 2>/dev/null || true
rm -f ~/Library/LaunchAgents/homebrew.mxcl.postgresql@*.plist

# Clean Homebrew
brew cleanup --prune=all
brew autoremove
```

---

## 3. Install PostgreSQL 17

1. **Install**:

   ```bash
   brew install postgresql@17
   ```

2. **Add `psql` to PATH** (Intel & Apple Silicon):

   ```bash
   echo 'export PATH="$(brew --prefix postgresql@17)/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Initialize the cluster**:

   ```bash
   initdb --locale=C -E UTF8 "$(brew --prefix)/var/postgresql@17"
   ```

4. **Start the service**:

   ```bash
   brew services start postgresql@17
   brew services list
   ```

---

## 4. Install TimescaleDB

1. **Tap the official repo**:

   ```bash
   brew tap timescale/tap
   ```

2. **Build & install** against PG 17:

   ```bash
   brew install --build-from-source timescale/tap/timescaledb
   ```

---

## 5. Link TimescaleDB Library Files

PostgreSQL preloads extensions from its `pkglibdir`. First, find Postgres’s expected path:

```bash
PG_LIB_DIR="$(pg_config --pkglibdir)"
echo "Postgres PKGLIBDIR → $PG_LIB_DIR"
```

Then symlink the TimescaleDB `.dylib` files:

```bash
TS_SRC="$(brew --cellar timescaledb)/2.21.0/lib/timescaledb/postgresql@17"
mkdir -p "$PG_LIB_DIR"

ln -sf "$TS_SRC"/timescaledb.dylib           "$PG_LIB_DIR"/timescaledb.dylib
ln -sf "$TS_SRC"/timescaledb-2.21.0.dylib     "$PG_LIB_DIR"/timescaledb-2.21.0.dylib
ln -sf "$TS_SRC"/timescaledb-tsl-2.21.0.dylib "$PG_LIB_DIR"/timescaledb-tsl-2.21.0.dylib
```

Restart to apply:

```bash
brew services restart postgresql@17
```

---

## 6. Install Control Files for TimescaleDB

Postgres needs `.control` and SQL files under its `share` tree:

```bash
TS_SHARE_DIR="$(brew --cellar timescaledb)/2.21.0/share/timescaledb/extension"
PG_SHARE_EXT="$(brew --prefix)/share/postgresql@17/extension"

mkdir -p "$PG_SHARE_EXT"
cp "$TS_SHARE_DIR"/timescaledb.control      "$PG_SHARE_EXT"/
cp "$TS_SHARE_DIR"/timescaledb--*.sql       "$PG_SHARE_EXT"/
cp "$TS_SHARE_DIR"/timescaledb-tsl--*.sql   "$PG_SHARE_EXT"/
```

Restart again:

```bash
brew services restart postgresql@17
```

---

## 7. Configure `postgresql.conf`

Ensure TimescaleDB loads on startup. In `$(brew --prefix)/var/postgresql@17/postgresql.conf`, verify:

```conf
shared_preload_libraries = 'timescaledb'        # requires restart
dynamic_library_path = '$libdir:/opt/homebrew/Cellar/timescaledb/2.21.0/lib/timescaledb/postgresql@17'
```

If you use `timescaledb-tune`, it writes at least the `shared_preload_libraries`:

```bash
timescaledb-tune --yes
```

---

## 8. Verification

1. **Service status**:

   ```bash
   brew services list  # postgresql@17 should be "started"
   ```

2. **Check live settings**:

   ```bash
   psql -d postgres -c "SHOW shared_preload_libraries; SHOW dynamic_library_path;"
   ```

   → Should show `timescaledb` and your custom library path.

3. **Create & list extension**:

   ```bash
   psql -d f1_telemetry -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"
   psql -d f1_telemetry -c "\dx"
   ```

   → `timescaledb` should appear in the extension list.

---

## 9. Troubleshooting

* **`could not access file "timescaledb"`**: Ensure symlinks/dynamic\_library\_path point to the exact `.dylib` location.
* **`extension "timescaledb" is not available`**: Confirm control files in `share/postgresql@17/extension`.
* **Plist errors**: Remove stale LaunchAgents and use manual `pg_ctl start` to isolate errors:

  ```bash
  rm -f ~/Library/LaunchAgents/homebrew.mxcl.postgresql@17.plist
  brew services cleanup
  ```

---

