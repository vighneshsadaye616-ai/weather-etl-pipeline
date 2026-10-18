-- name: monthly_summary
SELECT city,
       substr(date, 1, 7) AS month,
       ROUND(AVG(temp_max), 1) AS avg_max,
       ROUND(AVG(temp_min), 1) AS avg_min,
       ROUND(SUM(rain_mm), 1)  AS total_rain
FROM weather_daily
GROUP BY city, month
ORDER BY city, month;

-- name: hottest_days
SELECT city, date, temp_max
FROM weather_daily
ORDER BY temp_max DESC
LIMIT 10;

-- name: rainy_days_per_month
SELECT city,
       substr(date, 1, 7) AS month,
       SUM(CASE WHEN rain_mm > 1 THEN 1 ELSE 0 END) AS rainy_days
FROM weather_daily
GROUP BY city, month
ORDER BY city, month;

-- name: moving_avg_7day
SELECT city, date, temp_max,
       ROUND(AVG(temp_max) OVER (
           PARTITION BY city
           ORDER BY date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ), 1) AS avg_7day
FROM weather_daily
ORDER BY city, date;