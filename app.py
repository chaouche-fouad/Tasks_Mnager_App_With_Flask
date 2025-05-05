from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap5
import sqlite3
from datetime import datetime

app = Flask(__name__)
Bootstrap5(app)

# ------------------ Database Utilities ------------------


def get_db_connection():
    conn = sqlite3.connect('app.db', detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    """Create the tasks table if it doesn't exist."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_at TEXT
            );
        ''')
        conn.commit()


def insert_task(task, due_at=None):
    """Insert a new task."""
    if due_at:
        try:
            due_at = datetime.strptime(due_at, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            due_at = None
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO tasks (task, due_at) VALUES (?, ?)',
            (task, due_at)
        )
        conn.commit()


def get_all_tasks(filter=None, sort=None):
    """Retrieve all tasks with optional filtering and sorting."""
    conn = get_db_connection()
    query = 'SELECT * FROM tasks'
    conditions = []
    order_by = ''

    # Filtering
    if filter == 'completed':
        conditions.append('completed = 1')
    elif filter == 'active':
        conditions.append('completed = 0')
    elif filter == 'has-due-date':
        conditions.append('due_at IS NOT NULL')

    # Sorting
    if sort == 'added-date-asc':
        order_by = 'ORDER BY created_at ASC'
    elif sort == 'due-date-desc':
        order_by = 'ORDER BY due_at DESC'

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    if order_by:
        query += f' {order_by}'

    tasks = conn.execute(query).fetchall()
    conn.close()
    return tasks

# ------------------ App Routes ------------------


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        action = request.form.get('action')
        task_id = request.form.get('task_id')

        if action == 'add':
            task = request.form.get('task')
            due_date = request.form.get('due_date') or None
            if task:
                insert_task(task, due_date)

        elif action == 'delete' and task_id:
            with get_db_connection() as conn:
                conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                conn.commit()

        elif action == 'toggle' and task_id:
            with get_db_connection() as conn:
                conn.execute('''
                    UPDATE tasks
                    SET completed = NOT completed,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (task_id,))
                conn.commit()

        elif action == 'edit' and task_id:
            new_text = request.form.get('new_task')
            if new_text:
                with get_db_connection() as conn:
                    conn.execute('''
                        UPDATE tasks
                        SET task = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (new_text, task_id))
                    conn.commit()

        return redirect('/')

    # Handle GET request (filtering and sorting)
    task_filter = request.args.get('task_filter')
    task_sort = request.args.get('task_sort')
    tasks = get_all_tasks(filter=task_filter, sort=task_sort)

    return render_template('index.html', tasks=tasks)

# ------------------ Entry Point ------------------


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
