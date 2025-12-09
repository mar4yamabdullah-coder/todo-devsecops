# app/create_app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'todo.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    db.commit()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.secret_key = 'dev-secret-key'

    # --------------------------
    # Database init (Flask 3 fix)
    # --------------------------
    @app.before_request
    def setup():
        if not hasattr(app, "db_initialized"):
            init_db()
            app.db_initialized = True

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        db = get_db()
        cursor = db.execute('SELECT * FROM tasks WHERE user_id = ?', (session['user_id'],))
        tasks = cursor.fetchall()
        return render_template('index.html', tasks=tasks)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            if not username or not password:
                flash('Username and password required')
                return redirect(url_for('register'))
            db = get_db()
            try:
                db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                db.commit()
                flash('Registered! Please log in.')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already exists')
                return redirect(url_for('register'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            db = get_db()

            # SECURE
            cursor = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()

            if user:
                session['user_id'] = user['id']
                flash('Logged in')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials')
                return redirect(url_for('login'))
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('Logged out')
        return redirect(url_for('login'))

    @app.route('/add', methods=['POST'])
    def add_task():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        description = request.form.get('description', '').strip()
        if description:
            db = get_db()
            db.execute('INSERT INTO tasks (user_id, description) VALUES (?, ?)', (session['user_id'], description))
            db.commit()
            flash('Task added')
        return redirect(url_for('index'))

    @app.route('/delete/<int:task_id>', methods=['POST'])
    def delete_task(task_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        db = get_db()
        db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, session['user_id']))
        db.commit()
        flash('Task deleted')
        return redirect(url_for('index'))

    return app
