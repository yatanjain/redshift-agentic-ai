import sqlite3
from agent.database import get_connection


def get_all_tables(username: str = "default_user") -> str:
    """
    Returns a list of all tables the user can access.
    In Redshift, this would respect user-level permissions automatically.
    """
    try:
        conn = get_connection(username)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, type 
            FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "No tables found."

        result = "Available tables:\n"
        for row in rows:
            result += f"  - {row['name']} ({row['type']})\n"
        return result

    except Exception as e:
        return f"Error fetching tables: {str(e)}"


def get_ddl(table_name: str, username: str = "default_user") -> str:
    """
    Returns the DDL (column definitions) for a given table.
    Simulates Redshift's SHOW TABLE / pg_table_def behavior.
    """
    try:
        conn = get_connection(username)
        cursor = conn.cursor()

        # Check table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name.lower(),))

        if not cursor.fetchone():
            return f"Table '{table_name}' not found or you don't have access."

        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        conn.close()

        ddl = f"CREATE TABLE {table_name} (\n"
        col_defs = []
        for col in columns:
            pk = " PRIMARY KEY" if col["pk"] else ""
            nullable = "" if col["notnull"] else " NULL"
            default = f" DEFAULT {col['dflt_value']}" if col["dflt_value"] else ""
            col_defs.append(f"    {col['name']}  {col['type']}{pk}{nullable}{default}")
        ddl += ",\n".join(col_defs)
        ddl += "\n);"
        return ddl

    except Exception as e:
        return f"Error fetching DDL: {str(e)}"


def get_record_count(table_name: str, username: str = "default_user") -> str:
    """
    Returns the total number of records in a table.
    """
    try:
        conn = get_connection(username)
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) as total FROM {table_name}")
        result = cursor.fetchone()
        conn.close()
        return f"Table '{table_name}' has {result['total']:,} records."

    except Exception as e:
        return f"Error counting records: {str(e)}"


def get_table_owner(table_name: str, username: str = "default_user") -> str:
    """
    Returns the owner of a table.
    In SQLite all tables are owned by the DB file owner.
    In Redshift, this queries pg_tables for tableowner.
    """
    try:
        conn = get_connection(username)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name.lower(),))

        if not cursor.fetchone():
            return f"Table '{table_name}' not found or you don't have access."

        conn.close()
        # In SQLite, simulate owner as the current user
        # In Redshift: SELECT tableowner FROM pg_tables WHERE tablename = '{table_name}'
        return f"Table '{table_name}' is owned by: {username} (database administrator)"

    except Exception as e:
        return f"Error fetching table owner: {str(e)}"


def run_select_query(query: str, username: str = "default_user") -> str:
    """
    Executes a SELECT query and returns results.
    Enforces SELECT-only — no INSERT, UPDATE, DELETE, DROP allowed.
    In Redshift, user credentials ensure row/column level permissions.
    """
    # Security guard — only allow SELECT statements
    clean_query = query.strip().upper()
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
                 "ALTER", "TRUNCATE", "GRANT", "REVOKE"]

    for keyword in forbidden:
        if clean_query.startswith(keyword):
            return f"Access denied: '{keyword}' statements are not allowed. Only SELECT queries are permitted."

    if not clean_query.startswith("SELECT"):
        return "Only SELECT queries are allowed."

    try:
        conn = get_connection(username)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchmany(50)  # Limit to 50 rows for POC
        conn.close()

        if not rows:
            return "Query returned no results."

        # Format as readable table
        columns = [description[0] for description in cursor.description]
        result = " | ".join(columns) + "\n"
        result += "-" * len(result) + "\n"
        for row in rows:
            result += " | ".join(str(val) for val in row) + "\n"

        total = len(rows)
        result += f"\n({total} row{'s' if total != 1 else ''} returned)"
        if total == 50:
            result += " — limited to 50 rows"
        return result

    except Exception as e:
        return f"Query error: {str(e)}"


def get_column_info(table_name: str, username: str = "default_user") -> str:
    """
    Returns detailed column metadata for a table —
    name, data type, nullable, default value.
    """
    try:
        conn = get_connection(username)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        conn.close()

        if not columns:
            return f"Table '{table_name}' not found or has no columns."

        result = f"Column metadata for '{table_name}':\n\n"
        result += f"{'Column':<20} {'Type':<15} {'Nullable':<10} {'Default':<15} {'PK'}\n"
        result += "-" * 70 + "\n"
        for col in columns:
            nullable = "NO" if col["notnull"] else "YES"
            default = str(col["dflt_value"]) if col["dflt_value"] else "None"
            pk = "YES" if col["pk"] else ""
            result += f"{col['name']:<20} {col['type']:<15} {nullable:<10} {default:<15} {pk}\n"
        return result

    except Exception as e:
        return f"Error fetching column info: {str(e)}"
