from app.create_app import create_app
from flask import request
import sqlite3
import subprocess

app = create_app()


# --- Insecure SQL query for demo (SQL Injection vulnerability) ---
# This route is only for security demonstration and should NOT be used in production.
@app.route("/insecure-search")
def insecure_search():
    # User input: /insecure-search?title=Something
    title = request.args.get("title", "")

    # VULNERABLE SQL QUERY: string concatenation (classic SQL Injection pattern)
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    query = "SELECT id, title, description FROM todos WHERE title LIKE '%" + title + "%'"
    cursor.execute(query)  # <-- Vulnerable line

    rows = cursor.fetchall()
    conn.close()

    return {"results": rows}


# --- Insecure command execution for demo (Bandit will detect this) ---
@app.route("/insecure-shell")
def insecure_shell():
    # Example URL: /insecure-shell?cmd=ls
    cmd = request.args.get("cmd", "echo hello")

    # VULNERABLE: user input is passed directly to the shell
    subprocess.Popen("echo " + cmd, shell=True)  # <-- Bandit should flag this

    return {"status": "command executed (insecure)"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
