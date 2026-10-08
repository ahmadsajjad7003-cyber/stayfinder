from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'stayfinder-secret-key-change-this-later'

# ---------- Database Setup ----------
DB_FILE = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html', user=session.get('user_name'))

@app.route('/stays')
def stays():
    return render_template('stays.html', user=session.get('user_name'))

@app.route('/flights')
def flights():
    return render_template('flights.html', user=session.get('user_name'))

@app.route('/cars')
def cars():
    return render_template('cars.html', user=session.get('user_name'))

@app.route('/attractions')
def attractions():
    return render_template('attractions.html', user=session.get('user_name'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('Please fill all fields.', 'error')
            return redirect(url_for('signup'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('signup'))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute(
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                (name, email, generate_password_hash(password))
            )
            conn.commit()
            conn.close()
            flash('Account created! Please sign in.', 'success')
            return redirect(url_for('signin'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('Email already registered. Try signing in.', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT id, name, password FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash(f'Welcome back, {user[1]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('signin'))

    return render_template('signin.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please sign in first.', 'error')
        return redirect(url_for('signin'))
    return render_template('dashboard.html', user=session.get('user_name'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)