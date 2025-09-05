# flows/explore_fastf1_api.py

import fastf1
import inspect
import pandas as pd

def list_public(obj):
    return [name for name in dir(obj) if not name.startswith('_')]

def main():
    # 1) Version & top-level symbols
    print("FastF1 version:", fastf1.__version__)
    print("Top‑level in fastf1:", list_public(fastf1))

    # 2) Core function signatures
    print("\nfastf1.get_session signature:", inspect.signature(fastf1.get_session))
    print("fastf1.get_event   signature:", inspect.signature(fastf1.get_event))

    # 3) Submodules
    for sub in ('api', 'core', 'plotting'):
        module = getattr(fastf1, sub, None)
        if module:
            print(f"\nfastf1.{sub} members:", list_public(module))

    # 4) Instantiate & load a sample session
    year, gp, stype = 2025, 'Monaco', 'Race'
    print(f"\nLoading session {year} {gp} {stype}…")
    session = fastf1.get_session(year, gp, stype)
    session.load(telemetry=True, laps=True, weather=True)

    # 5) List session attributes
    public_attrs = [a for a in list_public(session) if not callable(getattr(session, a))]
    print("\nSession public attributes:", public_attrs)

    # 6) For each DataFrame, print its shape & columns
    for attr in public_attrs:
        val = getattr(session, attr)
        if isinstance(val, pd.DataFrame):
            print(f"\n→ {attr}: {val.shape[0]} rows × {len(val.columns)} cols")
            print("   Columns:", val.columns.tolist())

if __name__ == '__main__':
    main()
