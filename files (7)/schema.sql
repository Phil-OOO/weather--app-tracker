-- =============================================================================
-- schema.sql  —  Climate Temperature Tracker
-- =============================================================================
--
-- WHAT IS THIS FILE?
--   A plain SQL script that defines the shape of your database.
--   You don't NEED to run this manually — app.py creates the table
--   automatically via init_db().  Keep this file as documentation and
--   as a way to reset the database during development.
--
-- HOW TO RUN IT (optional):
--   Windows PowerShell :  python -c "import sqlite3; conn=sqlite3.connect('climate.db'); conn.executescript(open('schema.sql').read()); conn.close()"
--   Mac / Linux        :  sqlite3 climate.db < schema.sql
--
-- =============================================================================

-- DROP TABLE IF EXISTS lets you re-run this script from scratch.
-- WARNING: this deletes ALL existing data.  Remove it once you go to production.
DROP TABLE IF EXISTS readings;


-- CREATE TABLE defines a new table called "readings" with four columns.
CREATE TABLE readings (

    -- id: SQLite auto-assigns a unique integer to every new row.
    --     PRIMARY KEY means no two rows share the same id.
    --     AUTOINCREMENT means it always counts upward, never reuses a deleted id.
    id          INTEGER  PRIMARY KEY AUTOINCREMENT,

    -- city: A text string.  NOT NULL means the field is required —
    --       SQLite will reject any INSERT that leaves it empty.
    city        TEXT     NOT NULL,

    -- temperature: REAL stores a decimal number (e.g. 28.5 or -3.0).
    --              Stored as an IEEE 754 floating-point value.
    temperature REAL     NOT NULL,

    -- date: SQLite has no native DATE type, so we store dates as TEXT
    --       in "YYYY-MM-DD" format (ISO 8601).  Sorting TEXT in that
    --       format sorts chronologically, which is very handy.
    --       DEFAULT (date('now')) auto-fills today's date when omitted.
    date        TEXT     NOT NULL DEFAULT (date('now'))
);


-- Seed a few rows so the chart looks good on first launch.
-- (app.py's init_db() also does this check, so these only run
--  when you manually re-apply the schema from scratch.)
INSERT INTO readings (city, temperature, date) VALUES
    ('Accra',   30.5, '2024-06-01'),
    ('Accra',   31.2, '2024-06-02'),
    ('Accra',   29.8, '2024-06-03'),
    ('London',  18.0, '2024-06-01'),
    ('London',  17.5, '2024-06-02'),
    ('London',  19.1, '2024-06-03');
