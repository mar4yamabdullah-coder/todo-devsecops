# --- Insecure SQL query for demo (SQL Injection vulnerability) ---
# This route is only for security demonstration and should NOT be used in production.

from flask import request
import sqlite3   # <-- important for Bandit to detect SQL injection

@app.route("/insecure-search")
def insecure_search():
    # User input: /insecure-search?title=Something
    title = request.args.get("title", "")

    # VULNERABLE SQL QUERY (Bandit will detect this)
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    # SQL string concatenation (classic SQL Injection pattern)
    query = "SELECT id, title, description FROM todos WHERE title LIKE '%" + title + "%'"
    
    cursor.execute(query)  # <-- Vulnerable line Bandit detects

    rows = cursor.fetchall()
    conn.close()

    return {"results": rows}
