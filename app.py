from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_akn_key' # for sessions

DATABASE = 'akn.db'
PASSWORD = 'admin' # Simple password for now

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                date_created TEXT NOT NULL
            )
        ''')
        db.commit()

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT * FROM news ORDER BY id DESC')
    news = cur.fetchall()
    return render_template('index.html', news=news)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('admin.html', error='Неверный пароль')
    return render_template('admin.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute('INSERT INTO news (title, content, date_created) VALUES (?, ?, ?)', (title, content, date_created))
        db.commit()
        return redirect(url_for('dashboard'))
        
    cur = db.execute('SELECT * FROM news ORDER BY id DESC')
    news = cur.fetchall()
    return render_template('dashboard.html', news=news)

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    db = get_db()
    db.execute('DELETE FROM news WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    print("Сервер запущен! Перейдите по ссылке http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)