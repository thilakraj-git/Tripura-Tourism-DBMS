"""
Database Connection and Query Management for Tripura Terra
Provides robust SQLite connection management, WAL mode, strict foreign key enforcement,
transaction management, query profiling, and analytical query execution helpers.
"""

import sqlite3
import os
import time
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "tripura_terra.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Creates a connection with foreign keys and WAL mode enabled."""
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def init_db(db_path: str = DB_PATH, force: bool = False):
    """Initializes the database schema if tables do not exist or force=True."""
    if force and os.path.exists(db_path):
        os.remove(db_path)
        
    conn = get_connection(db_path)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

def execute_query(query: str, params: Tuple = (), db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Executes a SELECT query and returns rows as dictionaries."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        return rows
    finally:
        conn.close()

def execute_query_one(query: str, params: Tuple = (), db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    """Executes a SELECT query returning a single row as a dictionary."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def execute_update(query: str, params: Tuple = (), db_path: str = DB_PATH) -> int:
    """Executes an INSERT, UPDATE, or DELETE query and returns lastrowid or affected rows."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
    finally:
        conn.close()

def execute_transaction(operations: List[Tuple[str, Tuple]], db_path: str = DB_PATH) -> bool:
    """Executes a series of queries atomically inside an explicit transaction."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION;")
        for query, params in operations:
            cursor.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def profile_query(query: str, params: Tuple = (), db_path: str = DB_PATH) -> Dict[str, Any]:
    """Measures query execution time in milliseconds and retrieves EXPLAIN QUERY PLAN."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        
        # Get query plan
        cursor.execute(f"EXPLAIN QUERY PLAN {query}", params)
        plan_rows = [dict(r) for r in cursor.fetchall()]
        
        # Timed execution over multiple iterations for high precision
        iterations = 5
        start_time = time.perf_counter()
        for _ in range(iterations):
            cursor.execute(query, params)
            rows = cursor.fetchall()
        end_time = time.perf_counter()
        
        avg_time_ms = ((end_time - start_time) / iterations) * 1000.0
        
        return {
            "execution_time_ms": round(avg_time_ms, 3),
            "rows_returned": len(rows),
            "query_plan": plan_rows,
            "sample_results": [dict(r) for r in rows[:3]]
        }
    finally:
        conn.close()
