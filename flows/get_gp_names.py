import fastf1
import json

# 1) Grab the full schedule
sched = fastf1.get_event_schedule(2025)

# 2) See all the column names
print(sched.columns.tolist())

# 3) Get a concise summary of dtypes & non-null counts
print(sched.info())

# 4) Peek at the first few rows
df = (sched.head())

# 2. Take the first 5 rows and turn into a list of dicts
records = df.to_dict(orient='records')

# 3. Pretty-print as JSON (dates will be Python date objects, so we str() them)
print(json.dumps(
    [{k: (v.isoformat() if hasattr(v, 'isoformat') else v) for k, v in row.items()} 
     for row in records],
    indent=2
))

