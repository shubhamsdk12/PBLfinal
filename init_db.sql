-- Run this in PostgreSQL to create the database if it doesn't exist
-- Connect using: psql -U postgres -h localhost
-- Then run: \i init_db.sql

-- Create database (run this line manually if needed)
-- CREATE DATABASE spendwise;

-- Grant permissions (run after connecting to spendwise database)
-- psql -U postgres -h localhost -d spendwise

-- Tables will be auto-created by the application on startup
-- via Base.metadata.create_all() in app/main.py
