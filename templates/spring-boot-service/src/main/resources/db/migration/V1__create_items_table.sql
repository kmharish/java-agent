-- V1: Initial schema — items table
-- Replace 'items' with your domain entity. Never modify this file after it is applied.

CREATE TABLE IF NOT EXISTS items (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    status      VARCHAR(50)  NOT NULL DEFAULT 'ACTIVE',
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version     BIGINT       NOT NULL DEFAULT 0  -- optimistic locking
);

CREATE INDEX idx_items_status ON items (status);
