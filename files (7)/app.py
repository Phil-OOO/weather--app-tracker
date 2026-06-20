# =============================================================================
# app.py  —  Climate Temperature Tracker
# =============================================================================
#
# WHAT IS FLASK?
#   Flask is a "micro web framework". It listens for HTTP requests from a
#   browser, runs your Python functions, and sends HTML back as responses.
#
# HOW ROUTING WORKS:
#   @app.route("/some/path")   ← this decorator binds a URL to a function
#   def my_view():             ← Flask calls this when that URL is visited
#       return "Hello!"        ← whatever you return becomes the HTTP response
#
# =============================================================================

import sqlite3                   # Python's built-in SQLite driver — no install needed
import os                        # os.path.exists() lets us check if the DB file is there
from flask import (
    Flask,
    render_template,   # fills an HTML template with Python data and returns it
    request,           # gives access to incoming form data (request.form["field"])
    redirect,          # tells the browser to navigate to a different URL
    url_for,           # builds a URL from a function name — safer than hardcoding "/path"
)


# -----------------------------------------------------------------------------
# 1.  Create the Flask application object
# -----------------------------------------------------------------------------
# __name__ tells Flask where THIS file lives so it can find the /templates folder
app = Flask(__name__)

# The SQLite database will be stored in the same directory as app.py
DATABASE = "climate.db"


# -----------------------------------------------------------------------------
# 2.  Auto-create the database on first run
# -----------------------------------------------------------------------------
def init_db():
    """
    Creates the 'readings' table if it doesn't already exist, then seeds
    sample data so the chart isn't empty the very first time you open the app.

    KEY LESSON — "IF NOT EXISTS":
      CREATE TABLE IF NOT EXISTS means "only create this table when it's
      missing — skip silently if it already exists."
      This makes it safe to call init_db() every time the app starts.
    """
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id          INTEGER  PRIMARY KEY AUTOINCREMENT,
            city        TEXT     NOT NULL,
            temperature REAL     NOT NULL,
            date        TEXT     NOT NULL DEFAULT (date('now'))
        )
    """)
    # Column type notes:
    #   INTEGER  — whole numbers (1, 2, 3 …)
    #   REAL     — floating-point numbers (28.5, -3.0 …)
    #   TEXT     — strings
    #   PRIMARY KEY AUTOINCREMENT — SQLite picks a unique id for every new row
    #   DEFAULT (date('now')) — SQLite fills in today's date when none is given

    # Only insert sample rows when the table is completely empty
    row_count = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
    if row_count == 0:
        sample_data = [
            ("Accra",   30.5, "2024-06-01"),
            ("Accra",   31.2, "2024-06-02"),
            ("Accra",   29.8, "2024-06-03"),
            ("London",  18.0, "2024-06-01"),
            ("London",  17.5, "2024-06-02"),
            ("London",  19.1, "2024-06-03"),
        ]
        # executemany() is like execute() but runs the same SQL once per tuple
        conn.executemany(
            "INSERT INTO readings (city, temperature, date) VALUES (?, ?, ?)",
            sample_data,
        )
        print("📦  Database created and seeded with sample data.")

    conn.commit()   # flush all pending writes to disk
    conn.close()


# -----------------------------------------------------------------------------
# 3.  Helper — open a database connection
# -----------------------------------------------------------------------------
def get_db():
    """
    Opens and returns a connection to climate.db.

    WHY row_factory?
      By default sqlite3 returns rows as plain tuples: (1, "Accra", 30.5, …)
      Setting row_factory = sqlite3.Row lets you access columns by name:
        row["city"]   instead of   row[1]
      Much easier to read, and safer if you ever reorder columns.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------------------------------------------------------
# 4.  Route: GET /   —  show all readings + the chart
# -----------------------------------------------------------------------------
@app.route("/")                    # handles GET requests to the root URL
def index():
    """
    Reads every row from the database, then hands the data to the
    Jinja2 template (templates/index.html) which renders the final HTML.

    WHAT IS Jinja2?
      It's Flask's built-in template engine.  You write HTML with special
      placeholders like {{ variable }} or {% for row in readings %}, and
      Flask fills them in with real Python data before sending the page.
    """
    conn = get_db()

    # fetchall() returns a list of Row objects — one per database row
    # ORDER BY date ASC keeps the chart timeline left-to-right
    readings = conn.execute(
        "SELECT id, city, temperature, date FROM readings ORDER BY date ASC"
    ).fetchall()

    conn.close()   # always close when done — prevents file-lock issues

    # render_template() looks inside the /templates folder for "index.html"
    # Anything passed as a keyword argument becomes a variable in the template
    return render_template("index.html", readings=readings)


# -----------------------------------------------------------------------------
# 5.  Route: POST /submit   —  save a new reading
# -----------------------------------------------------------------------------
@app.route("/submit", methods=["POST"])   # only accept POST; GET → 405 error
def submit():
    """
    Handles the HTML form submission.

    THE POST / REDIRECT / GET PATTERN:
      After saving to the DB we don't render HTML directly — we redirect
      the browser back to GET /.  This prevents "form resubmission" warnings
      when the user hits refresh, because the last request becomes a GET.

    PARAMETERISED QUERIES (the ? placeholders):
      NEVER build SQL with f-strings:  f"INSERT … VALUES ('{city}')"
      A malicious city value like  '; DROP TABLE readings; --  would delete
      your whole database (SQL injection).
      The ? placeholders let sqlite3 escape the values safely for you.
    """
    # request.form is a dict-like object; keys match the <input name="…"> attributes
    city        = request.form["city"].strip()
    temperature = request.form["temperature"].strip()
    date        = request.form["date"].strip()

    # Basic server-side validation — never trust the browser alone
    if not city or not temperature or not date:
        return "All fields are required.", 400   # 400 = Bad Request

    conn = get_db()
    conn.execute(
        "INSERT INTO readings (city, temperature, date) VALUES (?, ?, ?)",
        (city, float(temperature), date),   # float() ensures we store a number
    )
    conn.commit()
    conn.close()

    # url_for("index") returns "/"  —  avoids hardcoding paths
    return redirect(url_for("index"))


# -----------------------------------------------------------------------------
# 6.  Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()            # create / verify the database before handling requests
    app.run(debug=True)  # debug=True → auto-reload on save, detailed error pages
                         # NEVER use debug=True on a public / production server!
