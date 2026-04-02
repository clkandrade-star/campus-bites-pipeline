import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables from the .env file (DB name, user, password)
load_dotenv()

# Build the database connection config from environment variables
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": "localhost",
    "port": 5432,
}

# SQL to create the orders table if it doesn't already exist.
# Each column type matches the data in the CSV.
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    order_id            INTEGER PRIMARY KEY,
    order_date          DATE,
    order_time          TIME,
    customer_segment    TEXT,
    order_value         NUMERIC(10, 2),
    cuisine_type        TEXT,
    delivery_time_mins  INTEGER,
    promo_code_used     BOOLEAN,
    is_reorder          BOOLEAN
);
"""

# SQL to insert rows in bulk. ON CONFLICT DO NOTHING makes it safe to re-run
# without creating duplicate records.
INSERT_SQL = """
INSERT INTO orders (
    order_id, order_date, order_time, customer_segment,
    order_value, cuisine_type, delivery_time_mins, promo_code_used, is_reorder
) VALUES %s
ON CONFLICT (order_id) DO NOTHING;
"""

# Path to the CSV file relative to this script's location
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "campus_bites_orders.csv")


def yes_no_to_bool(val):
    # Convert "Yes"/"No" strings from the CSV into Python booleans.
    # Guard against NaN (float) values that pandas inserts for missing cells.
    if not isinstance(val, str):
        return None
    return val.strip().lower() == "yes"


def main():
    # Read the CSV into a DataFrame
    df = pd.read_csv(CSV_PATH)

    # Convert Yes/No columns to booleans so they insert correctly as Postgres BOOLEAN
    df["promo_code_used"] = df["promo_code_used"].apply(yes_no_to_bool)
    df["is_reorder"] = df["is_reorder"].apply(yes_no_to_bool)

    # Convert the DataFrame to a list of plain tuples for psycopg2
    rows = list(df.itertuples(index=False, name=None))

    # Open a connection to the database
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        # `with conn` wraps everything in a transaction — rolls back on error
        with conn:
            with conn.cursor() as cur:
                # Create the table if it doesn't exist yet
                cur.execute(CREATE_TABLE_SQL)
                # Insert all rows in a single round-trip using execute_values
                execute_values(cur, INSERT_SQL, rows)
                print(f"Loaded {len(rows)} rows into the orders table.")
    finally:
        # Always close the connection, even if an error occurred
        conn.close()


if __name__ == "__main__":
    main()
