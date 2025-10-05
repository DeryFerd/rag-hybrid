# src/retrieval/sql_retriever.py
import os
import sqlite3
import re
from typing import List, Dict, Any
from google import genai
import sqlglot

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment.")
    return genai.Client(api_key=api_key)

def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """
    Convert schema dict into a clean prompt-friendly string.
    """
    lines = []
    for table, info in schema_info.items():
        lines.append(f"Table: {table}")
        lines.append(f"Schema: {info['schema']}")
        if info["sample_rows"]:
            lines.append("Sample rows (first 2):")
            for row in info["sample_rows"]:
                lines.append(f"  - {row}")
        lines.append("")
    return "\n".join(lines)

def generate_sql_with_gemini(nl_query: str, schema_info: Dict[str, Any]) -> str:
    """
    Use Gemini to generate safe SELECT-only SQL from natural language.
    """
    client = get_gemini_client()
    
    schema_str = format_schema_for_prompt(schema_info)
    
    prompt = f"""You are a SQL expert. Convert the user's question into a safe, read-only SQL query.
- Use ONLY the tables and columns provided in the schema.
- ONLY generate SELECT statements. NO INSERT, UPDATE, DELETE, DROP, ALTER, etc.
- Use parameterized queries if needed (but we'll handle params later).
- If unsure, return an empty string.

Schema:
{schema_str}

User question: {nl_query}

SQL query (only the SQL, no explanation):"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        #safety_settings={"harassment": "block_none"}  # reduce false positives
    )
    
    raw_sql = response.text.strip()
    # Clean common markdown
    if raw_sql.startswith("```sql"):
        raw_sql = raw_sql[7:]
    if raw_sql.endswith("```"):
        raw_sql = raw_sql[:-3]
    return raw_sql.strip()

def validate_sql_safe(sql: str) -> bool:
    """
    Basic SQL safety validator using sqlglot.
    """
    if not sql:
        return False
        
    # Must be a SELECT
    if not sql.lower().strip().startswith("select"):
        return False
        
    # Block dangerous keywords
    dangerous = ["drop", "delete", "insert", "update", "alter", "create", "exec", "execute", "truncate"]
    for word in dangerous:
        # Use regex to match whole words only
        if re.search(rf"\b{word}\b", sql, re.IGNORECASE):
            return False
            
    # Parse with sqlglot to check syntax
    try:
        parsed = sqlglot.parse(sql, dialect="sqlite")
        if parsed[0] is None:
            return False
    except Exception:
        return False
        
    return True

def execute_sql_safe(sql: str, db_path: str = "data/sql/music.db") -> List[Dict[str, Any]]:
    """
    Execute validated SQL and return results as list of dicts.
    """
    if not validate_sql_safe(sql):
        raise ValueError("SQL query failed safety validation.")
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # enables dict-like rows
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
    except Exception as e:
        conn.close()
        raise RuntimeError(f"SQL execution error: {e}")
    finally:
        conn.close()
        
    return result