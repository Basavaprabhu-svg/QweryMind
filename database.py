import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "querymind.db"
SQL_FILE = BASE_DIR / "database.sql"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SQL_FILE.read_text(encoding="utf-8"))
        conn.execute("""CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            sql_text TEXT NOT NULL,
            row_count INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()

def get_schema():
    with sqlite3.connect(DB_PATH) as conn:
        tables = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('EMPLOYEE','CUSTOMER','SALES')
            ORDER BY name
        """).fetchall()
        result = []
        for (table,) in tables:
            cols = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
            result.append({
                "table": table,
                "columns": [{"name": c[1], "type": c[2], "primary_key": bool(c[5])} for c in cols]
            })
        return result

def run_readonly_query(sql):
    # Open the database in read-only mode and add a second SQLite-level safeguard.
    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA query_only = ON")
        cursor = conn.execute(sql)
        columns = [item[0] for item in (cursor.description or [])]
        rows = [dict(row) for row in cursor.fetchmany(500)]
        return columns, rows
    finally:
        conn.close()

def save_history(question, sql, row_count, status):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO query_history(question, sql_text, row_count, status) VALUES (?, ?, ?, ?)",
            (question[:500], sql[:5000], row_count, status)
        )
        conn.commit()

def get_history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT id, question, sql_text, row_count, status, created_at
            FROM query_history ORDER BY id DESC LIMIT 20
        """).fetchall()
        return [dict(row) for row in rows]
