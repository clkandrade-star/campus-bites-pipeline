# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Campus Bites Pipeline loads 1,132 food delivery orders from a CSV file into a local PostgreSQL 16 database running in Docker. The goal is to enable ad-hoc SQL analysis of campus food delivery patterns without manual database setup.

## Setup

```bash
cp .env.example .env
docker compose up -d
python load_orders.py
```

## Common Commands

| Task | Command |
|------|---------|
| Start database | `docker compose up -d` |
| Stop (keep data) | `docker compose down` |
| Wipe data and restart | `docker compose down -v` |
| Connect via psql | `docker exec -it campus_bites_db psql -U postgres -d campus_bites` |
| Reload data | `python load_orders.py` (idempotent — safe to re-run) |

Database connection: `localhost:5432`, database `campus_bites`, user/password `postgres`.

## Architecture

The pipeline has two components:

**`load_orders.py`** — Python script that reads `data/campus_bites_orders.csv` and bulk-inserts into PostgreSQL using `psycopg2.extras.execute_values()`. Uses `ON CONFLICT (order_id) DO NOTHING` so re-runs are safe. Converts CSV "Yes"/"No" strings to PostgreSQL booleans before insertion. Credentials come from `.env` via `python-dotenv`.

**PostgreSQL (Docker)** — `postgres:16` container named `campus_bites_db`. The `./data` directory is mounted at `/data` inside the container. Data persists in the `postgres_data` Docker volume.

## `orders` Table Schema

| Column | Type |
|--------|------|
| `order_id` | INTEGER (PK) |
| `order_date` | DATE |
| `order_time` | TIME |
| `customer_segment` | TEXT |
| `order_value` | NUMERIC(10,2) |
| `cuisine_type` | TEXT |
| `delivery_time_mins` | INTEGER |
| `promo_code_used` | BOOLEAN |
| `is_reorder` | BOOLEAN |

## Dependencies

Python: `psycopg2-binary`, `pandas`, `python-dotenv`
External: Docker Desktop (required to run PostgreSQL)
