import sqlite3
import os
from contextlib import contextmanager
from utils.logger import get_logger

logger = get_logger("db_utils")

# Default to the data directory in the repo, but allow overriding via environment variable
DATA_DIR = os.environ.get('DATA_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'))
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, 'history.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'schema.sql')

@contextmanager
def get_db_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        yield conn
    finally:
        conn.close()

def init_db(db_path=DB_PATH, schema_path=SCHEMA_PATH):
    """Initialize the SQLite database with the schema and auto-migrate new columns."""
    with get_db_connection(db_path) as conn:
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
        
        # Migration: Ensure users table has role, subscription_plan, is_active
        cursor = conn.execute("PRAGMA table_info(users)")
        cols = [row['name'] for row in cursor.fetchall()]
        if 'role' not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        if 'subscription_plan' not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN subscription_plan TEXT DEFAULT 'free'")
        if 'is_active' not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")

        # Migration: Ensure user_settings table has active_format_mode and active_template_id
        cursor = conn.execute("PRAGMA table_info(user_settings)")
        us_cols = [row['name'] for row in cursor.fetchall()]
        if 'active_format_mode' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN active_format_mode TEXT DEFAULT 'default'")
        if 'active_template_id' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN active_template_id INTEGER DEFAULT NULL")
        if 'default_market' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN default_market TEXT DEFAULT 'UK'")
        if 'default_word_count' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN default_word_count TEXT DEFAULT '1500'")
        if 'default_tone' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN default_tone TEXT DEFAULT 'professional'")
        if 'default_keyword_density' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN default_keyword_density TEXT DEFAULT '1.2'")
        if 'airtable_api_key' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN airtable_api_key TEXT DEFAULT NULL")
        if 'airtable_base_id' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN airtable_base_id TEXT DEFAULT NULL")
        if 'airtable_table_name' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN airtable_table_name TEXT DEFAULT 'Links'")
        if 'theme_type' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN theme_type TEXT DEFAULT 'standard'")
        if 'seo_plugin' not in us_cols:
            conn.execute("ALTER TABLE user_settings ADD COLUMN seo_plugin TEXT DEFAULT 'none'")

        # Compatibility migration for older trusted_facts tables created before user_id defaulting was enforced.
        cursor = conn.execute("PRAGMA table_info(trusted_facts)")
        fact_cols = [row['name'] for row in cursor.fetchall()]
        if 'user_id' not in fact_cols:
            conn.execute("ALTER TABLE trusted_facts ADD COLUMN user_id INTEGER DEFAULT 1")
        conn.execute("UPDATE trusted_facts SET user_id = 1 WHERE user_id IS NULL")

        conn.commit()
    logger.info("Database initialized with column migrations.")
