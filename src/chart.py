"""Draws a temperature chart for Mumbai and saves it in reports/."""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
conn = sqlite3.connect(BASE / "weather.db")

df = pd.read_sql(
    """SELECT date, temp_max,
              AVG(temp_max) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS avg_7day
       FROM weather_daily
       WHERE city = 'Mumbai'
       ORDER BY date""",
    conn,
    parse_dates=["date"],
)
conn.close()

plt.figure(figsize=(12, 5))
plt.plot(df["date"], df["temp_max"], alpha=0.4, label="Daily max temp")
plt.plot(df["date"], df["avg_7day"], linewidth=2, label="7-day average")
plt.title("Mumbai Daily Maximum Temperature")
plt.ylabel("Temperature (°C)")
plt.legend()
plt.tight_layout()
plt.savefig(BASE / "reports" / "mumbai_temperature.png", dpi=150)
print("Saved reports/mumbai_temperature.png")