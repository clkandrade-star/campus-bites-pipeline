# Campus Bites Pipeline

A local Postgres database for digging into campus food delivery order data. Spin it up with one command, then query away.

## What you need

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — that's it

## Getting started

```bash
git clone <repo-url>
cd campus-bites-pipeline
cp .env.example .env
docker compose up -d
```

On first run, Postgres will automatically create the `orders` table and load all the data from the CSV. Subsequent starts skip that step — your data stays intact.

## Connecting

Use whatever Postgres client you like (DBeaver, TablePlus, psql, etc.):

| Setting  | Value          |
|----------|----------------|
| Host     | `localhost`    |
| Port     | `5432`         |
| Database | `campus_bites` |
| Username | `postgres`     |
| Password | `postgres`     |

Or jump straight into `psql`:

```bash
docker exec -it campus_bites_db psql -U postgres -d campus_bites
```

## The data

Everything lives in a single `orders` table:

| Column             | Type          |
|--------------------|---------------|
| order_id           | INTEGER (PK)  |
| order_date         | DATE          |
| order_time         | TIME          |
| customer_segment   | TEXT          |
| order_value        | NUMERIC(10,2) |
| cuisine_type       | TEXT          |
| delivery_time_mins | INTEGER       |
| promo_code_used    | BOOLEAN       |
| is_reorder         | BOOLEAN       |

## Some queries to get you started

```sql
-- What does the data look like?
SELECT * FROM orders LIMIT 10;

-- Revenue and order volume by cuisine
SELECT
    cuisine_type,
    COUNT(*)                        AS total_orders,
    ROUND(SUM(order_value), 2)      AS total_revenue,
    ROUND(AVG(order_value), 2)      AS avg_order_value
FROM orders
GROUP BY cuisine_type
ORDER BY total_orders DESC;

-- Which customer segments wait the longest?
SELECT
    customer_segment,
    ROUND(AVG(delivery_time_mins), 1) AS avg_delivery_mins
FROM orders
GROUP BY customer_segment
ORDER BY avg_delivery_mins;

-- How often are promo codes used?
SELECT
    ROUND(100.0 * SUM(promo_code_used::INT) / COUNT(*), 1) AS promo_pct
FROM orders;

-- Busiest days of the week
SELECT
    TO_CHAR(order_date, 'Day') AS day_of_week,
    COUNT(*)                   AS total_orders
FROM orders
GROUP BY day_of_week
ORDER BY MIN(EXTRACT(DOW FROM order_date));

-- Reorder rate by cuisine
SELECT
    cuisine_type,
    ROUND(100.0 * SUM(is_reorder::INT) / COUNT(*), 1) AS reorder_rate_pct
FROM orders
GROUP BY cuisine_type
ORDER BY reorder_rate_pct DESC;
```

## Resetting

Stop the container but keep your data:
```bash
docker compose down
```

Wipe everything and start fresh:
```bash
docker compose down -v
```
