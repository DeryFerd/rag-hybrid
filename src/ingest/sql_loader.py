# src/ingest/sql_loader.py
import sqlite3
import os
from typing import Dict, List, Any

def load_sqlite_schema_and_samples(db_path: str = "data/sql/music.db", sample_size: int = 2) -> Dict[str, Dict[str, Any]]:
    """
    Load schema (CREATE statements) and sample rows from SQLite DB.
    Returns dict: {table_name: {"schema": str, "sample_rows": list}}
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema_info = {}

    for table in tables:
        # Get CREATE statement
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}';")
        create_stmt = cursor.fetchone()
        schema = create_stmt[0] if create_stmt else ""

        # Get sample rows
        cursor.execute(f"SELECT * FROM {table} LIMIT {sample_size};")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table});")
        cols = [col[1] for col in cursor.fetchall()]
        
        sample_dicts = [dict(zip(cols, row)) for row in rows]

        schema_info[table] = {
            "schema": schema,
            "sample_rows": sample_dicts
        }

    conn.close()
    print(f"✅ Loaded schema & samples for {len(tables)} tables: {tables}")
    return schema_info