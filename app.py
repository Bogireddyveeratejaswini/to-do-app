from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from functools import wraps
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "taskflow-dev-secret-change-this")

DATABASE = "database.db"

CATEGORIES = ["Work", "Study", "Personal", "Shopping", "Other"]
PRIORITIES = ["High", "Medium", "Low"]


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            due_date TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Migrate older task databases safely.
    columns = [row["name"] for row in cursor.execute(
        "PRAGMA table_info(tasks)"
    ).fetchall()]

    if "category" not in columns:
        cursor.execute(
            "ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'Other'"
        )

    if "user_id" not in columns:
        cursor.execute(
            "ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id)"
        )

    conn.commit()
    conn.close()


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "error")
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password))
            )
            conn.commit()

            user = conn.execute(
                "SELECT id, name FROM users WHERE email = ?", (email,)
            ).fetchone()

            # First account takes over tasks created before login existed
            user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if user_count == 1:
                conn.execute(
                    "UPDATE tasks SET user_id = ? WHERE user_id IS NULL",
                    (user["id"],)
                )
                conn.commit()

            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            flash("Registration successful! Welcome to TO - DO.", "success")
            return redirect(url_for("index"))

        except sqlite3.IntegrityError:
            flash("This email is already registered.", "error")
        finally:
            conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Login successful!", "success")
            return redirect(url_for("index"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    conn = get_db()
    user_id = session["user_id"]

    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "All")
    category_filter = request.args.get("category", "All")
    sort = request.args.get("sort", "newest")

    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user_id]

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    if status_filter in ["Pending", "Completed"]:
        query += " AND status = ?"
        params.append(status_filter)

    if category_filter in CATEGORIES:
        query += " AND category = ?"
        params.append(category_filter)

    order_options = {
        "newest": "id DESC",
        "oldest": "id ASC",
        "priority": """
            CASE priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                ELSE 3
            END
        """,
        "due_date": "CASE WHEN due_date IS NULL OR due_date = '' THEN 1 ELSE 0 END, due_date ASC"
    }

    query += " ORDER BY " + order_options.get(sort, "id DESC")

    tasks = conn.execute(query, params).fetchall()

    all_tasks = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ?", (user_id,)
    ).fetchall()

    total = len(all_tasks)
    completed = sum(1 for task in all_tasks if task["status"] == "Completed")
    pending = total - completed

    # Pending tasks grouped by priority
    priority_counts = {
        priority: sum(
            1 for task in all_tasks
            if task["priority"] == priority and task["status"] == "Pending"
        )
        for priority in PRIORITIES
    }

    today = date.today().isoformat()

    conn.close()

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending,
        priority_counts=priority_counts,
        categories=CATEGORIES,
        search=search,
        status_filter=status_filter,
        category_filter=category_filter,
        sort=sort,
        today=today,
        user_name=session.get("user_name", "User")
    )


@app.route("/add", methods=["POST"])
@login_required
def add():
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "")
    category = request.form.get("category", "Other")

    if not title:
        flash("Task title cannot be empty.", "error")
        return redirect(url_for("index"))

    if priority not in PRIORITIES:
        priority = "Medium"

    if category not in CATEGORIES:
        category = "Other"

    conn = get_db()
    conn.execute("""
        INSERT INTO tasks (title, priority, due_date, status, category, user_id)
        VALUES (?, ?, ?, 'Pending', ?, ?)
    """, (title, priority, due_date, category, session["user_id"]))
    conn.commit()
    conn.close()

    flash("Task added successfully!", "success")
    return redirect(url_for("index"))


@app.route("/edit/<int:task_id>", methods=["POST"])
@login_required
def edit(task_id):
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "")
    category = request.form.get("category", "Other")

    if not title:
        flash("Task title cannot be empty.", "error")
        return redirect(url_for("index"))

    if priority not in PRIORITIES:
        priority = "Medium"

    if category not in CATEGORIES:
        category = "Other"

    conn = get_db()
    conn.execute("""
        UPDATE tasks
        SET title = ?, priority = ?, due_date = ?, category = ?
        WHERE id = ? AND user_id = ?
    """, (title, priority, due_date, category, task_id, session["user_id"]))
    conn.commit()
    conn.close()

    flash("Task updated successfully!", "success")
    return redirect(url_for("index"))


# POST only: the page uses forms/buttons for these, and changing data
# through a plain link (GET) is unsafe
@app.route("/toggle/<int:task_id>", methods=["POST"])
@login_required
def toggle(task_id):
    conn = get_db()
    task = conn.execute("""
        SELECT status FROM tasks
        WHERE id = ? AND user_id = ?
    """, (task_id, session["user_id"])).fetchone()

    if task:
        new_status = (
            "Completed" if task["status"] == "Pending" else "Pending"
        )
        conn.execute("""
            UPDATE tasks SET status = ?
            WHERE id = ? AND user_id = ?
        """, (new_status, task_id, session["user_id"]))
        conn.commit()

    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete(task_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    )
    conn.commit()
    conn.close()

    flash("Task deleted.", "success")
    return redirect(url_for("index"))


# Runs on every start, so it also works with "flask run"
init_db()

if __name__ == "__main__":
    app.run(debug=True)