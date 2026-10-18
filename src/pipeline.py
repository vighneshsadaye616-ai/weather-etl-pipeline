"""Daily weather ETL pipeline: collect -> clean -> load -> report."""
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "weather.db"

# Make sure the folders exist (Git does not store empty folders)
for folder in ["logs", "data/raw", "reports"]:
    (BASE / folder).mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=BASE / "logs" / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# Add or remove cities here: "Name": (latitude, longitude)
CITIES = {
    "Mumbai": (19.07, 72.87),
    "Delhi": (28.61, 77.21),
    "Bengaluru": (12.97, 77.59),
}

COLUMN_NAMES = {
    "time": "date",
    "temperature_2m_max": "temp_max",
    "temperature_2m_min": "temp_min",
    "precipitation_sum": "rain_mm",
}


# ---------- 1. COLLECT ----------
def collect():
    frames = []
    for city, (lat, lon) in CITIES.items():
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "past_days": 30,
            "forecast_days": 1,
            "timezone": "Asia/Kolkata",
        }
        r = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=30)
        r.raise_for_status()
        df = pd.DataFrame(r.json()["daily"]).rename(columns=COLUMN_NAMES)
        df["city"] = city
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)
    raw_file = BASE / "data" / "raw" / f"weather_{datetime.now():%Y%m%d}.csv"
    data.to_csv(raw_file, index=False)  # keep a raw backup
    logging.info("Collected %d rows for %d cities", len(data), len(CITIES))
    return data


# ---------- 2. CLEAN ----------
def clean(df):
    df = df.drop_duplicates(subset=["city", "date"]).copy()
    df["rain_mm"] = df["rain_mm"].fillna(0)
    df = df.dropna(subset=["temp_max", "temp_min"])
    logging.info("After cleaning: %d rows", len(df))
    return df


# ---------- 3. LOAD ----------
def load(df):
    conn = sqlite3.connect(DB_PATH)
    conn.executescript((BASE / "sql" / "schema.sql").read_text())

    cols = ["city", "date", "temp_max", "temp_min", "rain_mm"]
    out = df[cols].astype(object).where(df[cols].notnull(), None)
    rows = out.values.tolist()

    conn.executemany(
        """INSERT INTO weather_daily (city, date, temp_max, temp_min, rain_mm)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(city, date) DO UPDATE SET
               temp_max = excluded.temp_max,
               temp_min = excluded.temp_min,
               rain_mm  = excluded.rain_mm""",
        rows,
    )
    conn.commit()
    conn.close()
    logging.info("Loaded %d rows into database", len(rows))


# ---------- 4. REPORT ----------
def report():
    text = (BASE / "sql" / "queries.sql").read_text()
    conn = sqlite3.connect(DB_PATH)
    for block in text.split("-- name:")[1:]:
        name, query = block.split("\n", 1)
        result = pd.read_sql(query, conn)
        out = BASE / "reports" / f"{name.strip()}_{datetime.now():%Y%m%d}.csv"
        result.to_csv(out, index=False)
    conn.close()
    logging.info("Reports generated")


# ---------- RUN ----------
if __name__ == "__main__":
    try:
        data = clean(collect())
        load(data)
        report()
        logging.info("Pipeline finished successfully")
        print("Pipeline finished successfully. Check weather.db, reports/ and logs/")
    except Exception as e:
        logging.error("Pipeline failed: %s", e)
        print("Pipeline FAILED:", e)
        raise