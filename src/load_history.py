"""Downloads ~3 years of daily weather for every city and loads it into the database."""
from datetime import date, timedelta

import pandas as pd
import requests

from pipeline import BASE, CITIES, COLUMN_NAMES, clean, load

START = "2023-01-01"
END = (date.today() - timedelta(days=5)).isoformat()  # archive data lags a few days

frames = []
for city, (lat, lon) in CITIES.items():
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START,
        "end_date": END,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Asia/Kolkata",
    }
    r = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params, timeout=60)
    r.raise_for_status()
    df = pd.DataFrame(r.json()["daily"]).rename(columns=COLUMN_NAMES)
    df["city"] = city
    df.to_csv(BASE / "data" / "raw" / f"{city.lower()}_history.csv", index=False)
    frames.append(df)
    print(f"{city}: {len(df)} rows downloaded")

all_data = pd.concat(frames, ignore_index=True)
load(clean(all_data))
print("Done. Total rows loaded:", len(all_data))