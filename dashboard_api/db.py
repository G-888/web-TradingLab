import logging
import os
import sqlite3
from contextlib import contextmanager
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - optional until DATABASE_URL is used
    psycopg = None
    dict_row = None

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "data/local_dashboard_gold_bot.db")
DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("SUPABASE_DB_URL")
    or os.getenv("POSTGRES_URL")
)


def using_postgres() -> bool:
    return bool(DATABASE_URL)


def _postgres_url() -> str:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    parsed = urlparse(DATABASE_URL)
    query = dict(parse_qsl(parsed.query))
    if "sslmode" not in query:
        query["sslmode"] = "require"

    return urlunparse(parsed._replace(query=urlencode(query)))


def _convert_placeholders(query: str) -> str:
    return query.replace("?", "%s")


POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    chat_id BIGINT PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    ai_mode TEXT DEFAULT 'institutional',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL DEFAULT 0,
    direction TEXT NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    alert_type TEXT DEFAULT 'price',
    triggered INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS summary_schedules (
    chat_id BIGINT PRIMARY KEY,
    time_utc TEXT NOT NULL,
    last_sent TEXT
);

CREATE TABLE IF NOT EXISTS user_preferences (
    chat_id BIGINT PRIMARY KEY,
    ai_mode TEXT DEFAULT 'institutional',
    preferred_timeframe TEXT DEFAULT '1H',
    show_fib INTEGER DEFAULT 1,
    show_smc INTEGER DEFAULT 1,
    show_sessions INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS conversation_state (
    chat_id BIGINT PRIMARY KEY,
    state_key TEXT,
    state_data TEXT,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS backtest_runs (
    id BIGSERIAL PRIMARY KEY,
    strategy TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    lookback TEXT NOT NULL,
    total_trades INTEGER DEFAULT 0,
    win_rate DOUBLE PRECISION DEFAULT 0,
    profit_factor DOUBLE PRECISION DEFAULT 0,
    max_drawdown DOUBLE PRECISION DEFAULT 0,
    sharpe DOUBLE PRECISION DEFAULT 0,
    total_pnl DOUBLE PRECISION DEFAULT 0,
    ran_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS backtest_trades (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES backtest_runs(id),
    direction TEXT,
    entry DOUBLE PRECISION,
    sl DOUBLE PRECISION,
    tp DOUBLE PRECISION,
    rr_ratio DOUBLE PRECISION,
    rr_actual DOUBLE PRECISION,
    pnl DOUBLE PRECISION,
    duration_bars INTEGER,
    exit_reason TEXT,
    strategy TEXT,
    session TEXT,
    regime TEXT,
    confidence DOUBLE PRECISION,
    mae DOUBLE PRECISION,
    mfe DOUBLE PRECISION,
    timestamp TEXT
);

CREATE TABLE IF NOT EXISTS signal_history (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT DEFAULT 'XAUUSD',
    strategy TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    direction TEXT NOT NULL,
    confidence DOUBLE PRECISION DEFAULT 0,
    regime TEXT,
    session TEXT,
    entry_price DOUBLE PRECISION,
    recorded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS optimization_runs (
    id BIGSERIAL PRIMARY KEY,
    strategy TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    lookback TEXT NOT NULL,
    total_combos INTEGER DEFAULT 0,
    viable_combos INTEGER DEFAULT 0,
    best_params TEXT,
    best_score DOUBLE PRECISION DEFAULT 0,
    robustness_score DOUBLE PRECISION DEFAULT 0,
    stability_score DOUBLE PRECISION DEFAULT 0,
    overfit_warning TEXT,
    ran_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS performance_snapshots (
    id BIGSERIAL PRIMARY KEY,
    strategy TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    win_rate DOUBLE PRECISION DEFAULT 0,
    profit_factor DOUBLE PRECISION DEFAULT 0,
    expectancy DOUBLE PRECISION DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    vol_adj_score DOUBLE PRECISION DEFAULT 0,
    recorded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regime_statistics (
    id BIGSERIAL PRIMARY KEY,
    strategy TEXT NOT NULL,
    regime TEXT NOT NULL,
    trades INTEGER DEFAULT 0,
    win_rate DOUBLE PRECISION DEFAULT 0,
    total_pnl DOUBLE PRECISION DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS strategy_benchmark_runs (
    id BIGSERIAL PRIMARY KEY,
    run_type TEXT,
    symbol TEXT,
    timeframe TEXT,
    strategies TEXT,
    lookback TEXT,
    started_at TEXT,
    completed_at TEXT,
    status TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS strategy_benchmark_results (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT REFERENCES strategy_benchmark_runs(id),
    strategy_id TEXT,
    strategy_name TEXT,
    symbol TEXT,
    timeframe TEXT,
    market_regime TEXT,
    session TEXT,
    total_trades INTEGER,
    wins INTEGER,
    losses INTEGER,
    win_rate DOUBLE PRECISION,
    profit_factor DOUBLE PRECISION,
    max_drawdown DOUBLE PRECISION,
    net_pnl DOUBLE PRECISION,
    expectancy DOUBLE PRECISION,
    sharpe DOUBLE PRECISION,
    avg_rr DOUBLE PRECISION,
    score DOUBLE PRECISION,
    rank INTEGER,
    result_json TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS forward_test_sessions (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    strategies_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    stopped_at TIMESTAMPTZ,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS forward_test_trades (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES forward_test_sessions(id),
    strategy_id TEXT NOT NULL,
    strategy_name TEXT,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    direction TEXT NOT NULL,
    entry_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    entry_price DOUBLE PRECISION,
    stop_loss DOUBLE PRECISION,
    take_profit DOUBLE PRECISION,
    status TEXT NOT NULL DEFAULT 'OPEN',
    result TEXT,
    confidence DOUBLE PRECISION,
    exit_time TIMESTAMPTZ,
    exit_price DOUBLE PRECISION,
    pnl DOUBLE PRECISION,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
"""


SQLITE_DASHBOARD_SCHEMA = """
CREATE TABLE IF NOT EXISTS forward_test_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    strategies_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    stopped_at DATETIME,
    notes TEXT
);

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
);
"""


def init_postgres_db(conn) -> None:
    with conn.cursor() as cursor:
        for statement in [s.strip() for s in POSTGRES_SCHEMA.split(";") if s.strip()]:
            cursor.execute(statement)
    conn.commit()


def init_dashboard_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SQLITE_DASHBOARD_SCHEMA)
    conn.commit()


@contextmanager
def get_db_connection():
    if using_postgres():
        if psycopg is None:
            logger.error("DATABASE_URL is configured but psycopg is not installed")
            yield None
            return
        conn = None
        try:
            conn = psycopg.connect(_postgres_url(), row_factory=dict_row)
            init_postgres_db(conn)
            yield conn
        except Exception as e:
            logger.error("Failed to connect to Postgres database: %s", e)
            yield None
        finally:
            if conn:
                conn.close()
        return

    if not os.path.exists(DB_PATH):
        logger.warning("Database not found at %s", DB_PATH)
        yield None
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        init_dashboard_db(conn)
        yield conn
    except Exception as e:
        logger.error("Failed to connect to SQLite database: %s", e)
        yield None
    finally:
        if conn:
            conn.close()


def fetch_all(query: str, params: tuple = ()) -> list[dict]:
    with get_db_connection() as conn:
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(_convert_placeholders(query) if using_postgres() else query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.warning("Database fetch_all error: %s for query: %s", e, query)
            return []


def fetch_one(query: str, params: tuple = ()) -> dict | None:
    with get_db_connection() as conn:
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(_convert_placeholders(query) if using_postgres() else query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.warning("Database fetch_one error: %s for query: %s", e, query)
            return None


def execute_query(query: str, params: tuple = ()) -> int | None:
    with get_db_connection() as conn:
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            sql = _convert_placeholders(query) if using_postgres() else query
            if using_postgres() and query.lstrip().upper().startswith("INSERT") and "RETURNING" not in query.upper():
                sql = f"{sql} RETURNING id"
                cursor.execute(sql, params)
                row = cursor.fetchone()
                conn.commit()
                return row["id"] if row else None

            cursor.execute(sql, params)
            conn.commit()
            return getattr(cursor, "lastrowid", None)
        except Exception as e:
            logger.error("Database execute_query error: %s for query: %s", e, query)
            return None


def check_db_status() -> dict:
    if using_postgres():
        ok = fetch_one("SELECT 1 AS ok") is not None
        return {
            "database_connected": ok,
            "database_path": "supabase-postgres",
        }

    exists = os.path.exists(DB_PATH)
    return {
        "database_connected": exists,
        "database_path": DB_PATH,
    }
