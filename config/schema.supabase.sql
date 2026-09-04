-- PostgreSQL Schema for Supabase
-- Compatible with Python SQLAlchemy models

-- =========================================
-- USERS
-- =========================================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    subscription_plan TEXT NOT NULL DEFAULT 'free',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Keep existing Supabase deployments compatible with the current SQLAlchemy model.
ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT NOT NULL DEFAULT 'user';
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_plan TEXT NOT NULL DEFAULT 'free';
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- =========================================
-- USER SETTINGS
-- =========================================
CREATE TABLE IF NOT EXISTS user_settings (
    user_id BIGINT PRIMARY KEY,
    wp_url TEXT,
    wp_username TEXT,
    wp_app_password TEXT,
    theme_type TEXT DEFAULT 'standard',
    seo_plugin TEXT DEFAULT 'none',
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================
-- SESSIONS
-- =========================================
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================
-- LINKS
-- =========================================
CREATE TABLE IF NOT EXISTS links (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    url TEXT NOT NULL,
    game_name TEXT,
    provider TEXT,
    status TEXT DEFAULT 'New',
    status_reason TEXT,
    featured_image TEXT,
    description_image TEXT,
    login_image TEXT,
    transaction_image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================
-- PUBLISH HISTORY
-- =========================================
CREATE TABLE IF NOT EXISTS publish_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    game_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    article_id TEXT,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, game_name, provider),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================
-- TRUSTED FACTS
-- =========================================
CREATE TABLE IF NOT EXISTS trusted_facts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL DEFAULT 1,
    game_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    rtp REAL,
    volatility TEXT,
    max_win TEXT,
    release_date TEXT,
    min_bet REAL,
    max_bet REAL,
    UNIQUE(user_id, game_name, provider),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================
-- IMAGE LICENSES
-- =========================================
CREATE TABLE IF NOT EXISTS image_licenses (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    game_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    file_path TEXT NOT NULL,
    license_type TEXT NOT NULL,
    license_notes TEXT,
    UNIQUE(user_id, game_name, provider),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================
-- INDEXES (Optional but recommended)
-- =========================================
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_links_user_id ON links(user_id);
CREATE INDEX IF NOT EXISTS idx_links_status ON links(status);
CREATE INDEX IF NOT EXISTS idx_publish_history_user_id ON publish_history(user_id);
CREATE INDEX IF NOT EXISTS idx_trusted_facts_user_id ON trusted_facts(user_id);
CREATE INDEX IF NOT EXISTS idx_image_licenses_user_id ON image_licenses(user_id);
