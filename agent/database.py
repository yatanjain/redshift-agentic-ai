import sqlite3
import os

DB_PATH = "poc_database.db"


def get_connection(username: str = "default_user"):
    """
    Returns a SQLite connection.
    In production Redshift, this would use the user's own credentials
    so permissions are enforced at the database level.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def setup_sample_database():
    """
    Creates sample tables with realistic data to simulate a Redshift environment.
    Run this once to initialize the POC database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id     INTEGER PRIMARY KEY,
            customer_id  INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity     INTEGER NOT NULL,
            unit_price   REAL NOT NULL,
            order_date   TEXT NOT NULL,
            region       TEXT NOT NULL,
            status       TEXT NOT NULL
        )
    """)

    # Create customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id   INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email         TEXT NOT NULL,
            country       TEXT NOT NULL,
            segment       TEXT NOT NULL,
            created_date  TEXT NOT NULL
        )
    """)

    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id   INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category     TEXT NOT NULL,
            unit_price   REAL NOT NULL,
            stock_qty    INTEGER NOT NULL,
            supplier     TEXT NOT NULL
        )
    """)

    # Insert sample customers
    cursor.executemany("""
        INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?,?)
    """, [
        (1, "Alice Johnson",  "alice@example.com",  "USA",    "Enterprise", "2022-01-15"),
        (2, "Bob Smith",      "bob@example.com",    "UK",     "SMB",        "2022-03-22"),
        (3, "Carol Williams", "carol@example.com",  "Canada", "Enterprise", "2022-05-10"),
        (4, "David Brown",    "david@example.com",  "USA",    "SMB",        "2023-01-08"),
        (5, "Eva Martinez",   "eva@example.com",    "Germany","Enterprise", "2023-04-17"),
    ])

    # Insert sample products
    cursor.executemany("""
        INSERT OR IGNORE INTO products VALUES (?,?,?,?,?,?)
    """, [
        (1, "Laptop Pro",    "Electronics", 1200.00, 45,  "TechSupply Co"),
        (2, "Office Chair",  "Furniture",    350.00, 120, "FurniturePlus"),
        (3, "Keyboard",      "Electronics",   85.00, 200, "TechSupply Co"),
        (4, "Monitor 27in",  "Electronics",  420.00,  60, "ScreenWorld"),
        (5, "Standing Desk", "Furniture",    650.00,  30, "FurniturePlus"),
    ])

    # Insert sample orders
    cursor.executemany("""
        INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?,?,?)
    """, [
        (1001, 1, "Laptop Pro",    2, 1200.00, "2024-01-10", "West",  "Completed"),
        (1002, 2, "Office Chair",  5,  350.00, "2024-01-15", "East",  "Completed"),
        (1003, 3, "Keyboard",     10,   85.00, "2024-02-01", "North", "Completed"),
        (1004, 1, "Monitor 27in",  3,  420.00, "2024-02-14", "West",  "Pending"),
        (1005, 4, "Standing Desk", 1,  650.00, "2024-03-05", "South", "Completed"),
        (1006, 5, "Laptop Pro",    4, 1200.00, "2024-03-20", "East",  "Completed"),
        (1007, 2, "Keyboard",      7,   85.00, "2024-04-01", "East",  "Pending"),
        (1008, 3, "Monitor 27in",  2,  420.00, "2024-04-18", "North", "Completed"),
        (1009, 4, "Office Chair",  3,  350.00, "2024-05-02", "South", "Cancelled"),
        (1010, 5, "Standing Desk", 2,  650.00, "2024-05-15", "East",  "Completed"),
    ])

    conn.commit()
    conn.close()
    print("Sample database created successfully at:", DB_PATH)


if __name__ == "__main__":
    setup_sample_database()
