from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret123'  # required for login session

# ---------------- DATABASE ----------------
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    # Inventory table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create default user (only once)
    user = conn.execute("SELECT * FROM users WHERE username = ?", ('admin',)).fetchone()
    if not user:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))

    conn.commit()
    conn.close()

# ---------------- LOGIN REQUIRED ----------------
def login_required():
    if 'user' not in session:
        return False
    return True

# ---------------- ROUTES ----------------

# Login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('inventory'))

    return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Inventory page
@app.route('/inventory')
def inventory():
    if not login_required():
        return redirect(url_for('login'))

    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()

    return render_template('index.html', items=items)


# Add item
@app.route('/add', methods=('POST',))
def add():
    if not login_required():
        return redirect(url_for('login'))

    name = request.form['name']
    quantity = request.form['quantity']

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO items (name, quantity) VALUES (?, ?)',
        (name, quantity)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('inventory'))


# Update item
@app.route('/update/<int:id>', methods=('GET', 'POST'))
def update(id):
    if not login_required():
        return redirect(url_for('login'))

    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        quantity = request.form['quantity']

        conn.execute(
            'UPDATE items SET quantity = ? WHERE id = ?',
            (quantity, id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('inventory'))

    conn.close()
    return render_template('update.html', item=item)


# Delete item
@app.route('/delete/<int:id>')
def delete(id):
    if not login_required():
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('inventory'))


# Run app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)