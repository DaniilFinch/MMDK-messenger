import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'mmdk_ultra_secret_key'


# Функция для подключения к БД
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Создание таблицы при старте
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/qw')
def qw():
    now = datetime.now()
    return render_template('qw.html', current_date=now.strftime("%d.%m.%Y"), current_year=now.year)


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Хешируем пароль для безопасности
    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                     (username, email, hashed_password))
        conn.commit()
        flash('Регистрация успешна! Теперь войдите.')
    except sqlite3.IntegrityError:
        flash('Ошибка: этот Email уже зарегистрирован.')
    finally:
        conn.close()

    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('profile')) # ИСПРАВЛЕНО
    else:
        flash('Неверный email или пароль.')
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы.')
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Пожалуйста, войдите в аккаунт.")
        return redirect(url_for('index'))


    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
