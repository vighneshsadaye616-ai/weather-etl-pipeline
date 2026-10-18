# Automated Weather ETL Pipeline

A Python + SQL pipeline that pulls daily weather data for Mumbai, Delhi, Chennai, and Bengaluru from the Open-Meteo API, cleans it, stores it in SQLite, runs analytical SQL queries, and produces CSV reports and a chart every day.

## Tools
Python, pandas, requests, SQLite, SQL (window functions), matplotlib, Task Scheduler/cron, Git

## Pipeline
API → clean (dedupe, handle nulls) → SQLite (UNIQUE + upsert) → SQL reports → CSV/PNG

## Folder structure
sql/ (schema and queries), src/ (python scripts), data/raw/ (raw backups), reports/ (outputs), logs/

## How to run
```powershell
pip install -r requirements.txt
python src/load_history.py
python src/pipeline.py
python src/chart.py
```

## Key SQL concepts used
GROUP BY, aggregates, CASE WHEN, window functions (7-day moving average), UPSERT

## Results
![Weather Trends Chart](reports/weather_trends.png)

## Data source
Open-Meteo API: https://open-meteo.com/
