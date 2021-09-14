CREATE DATABASE shopify;
\c shopify

CREATE USER flask;

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(16),
    token_hash VARCHAR(256),

    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS images ( 
    owner_id VARCHAR(16),
    filename VARCHAR(128),
    is_public BOOLEAN,
    content_type VARCHAR(64),
    data bytea,

    PRIMARY KEY (owner_id, filename)
);

GRANT CONNECT ON DATABASE shopify TO flask;
GRANT USAGE ON SCHEMA public TO flask;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO flask;
