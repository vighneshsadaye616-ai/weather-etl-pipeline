CREATE TABLE IF NOT EXISTS weather_daily (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    city      TEXT NOT NULL,
    date      TEXT NOT NULL,
    temp_max  REAL,
    temp_min  REAL,
    rain_mm   REAL,
    loaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (city, date)
);