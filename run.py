from app.create_app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
# --- Insecure SQL query for demo (SQL Injection vulnerability) ---
# This route is only for security demonstration and should NOT be used in production.

from flask import request

@app.route("/insecure-search")
def insecure_search():
    # Get user input from the query string: /insecure-search?title=Something
    title = request.args.get("title", "")

    # WARNING: This query is vulnerable to SQL Injection because it uses string concatenation
    query = f"SELECT id, title, description FROM todos WHERE title LIKE '%{title}%'"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)   # <-- Vulnerable line
    rows = cursor.fetchall()
    conn.close()

    # For demo, just return the rows as plain text
    return {"results": [dict(row) for row in rows]}

