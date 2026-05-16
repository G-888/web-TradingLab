import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "data/local_dashboard_gold_bot.db")

def init_dashboard_db(conn: sqlite3.Connection):
    try:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS forward_test_sessions')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forward_test_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                strategies_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                stopped_at DATETIME,
                notes TEXT
            )
        ''')
        cursor.execute('DROP TABLE IF EXISTS forward_test_trades')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forward_test_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                strategy_id TEXT NOT NULL,
                strategy_name TEXT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                status TEXT NOT NULL DEFAULT 'OPEN',
                result TEXT,
                confidence REAL,
                exit_time DATETIME,
                exit_price REAL,
                pnl REAL,
                reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES forward_test_sessions(id)
            )
        ''')
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to init dashboard tables: {e}")

def get_db_connection() -> sqlite3.Connection | None:
    if not os.path.exists(DB_PATH):
        logger.warning(f"Database not found at {DB_PATH}")
        return None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        init_dashboard_db(conn)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

def fetch_all(query: str, params: tuple = ()) -> list[dict]:
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.OperationalError as e:
        logger.warning(f"SQLite error (table/column might be missing): {e} for query: {query}")
        return []
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return []
    finally:
        conn.close()

def fetch_one(query: str, params: tuple = ()) -> dict | None:
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.OperationalError as e:
        logger.warning(f"SQLite error (table/column might be missing): {e} for query: {query}")
        return None
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None
    finally:
        conn.close()

def execute_query(query: str, params: tuple = ()) -> int | None:
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return None
    finally:
        conn.close()

def check_db_status() -> dict:
    exists = os.path.exists(DB_PATH)
    return {
        "database_connected": exists,
        "database_path": DB_PATH
    }
