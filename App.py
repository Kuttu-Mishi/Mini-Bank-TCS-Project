# app.py
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret123'  # Session key

def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            return redirect('/dashboard')
        else:
            return "Invalid login"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('dashboard.html', user=user)

@app.route('/send', methods=['GET', 'POST'])
def send_money():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        amount = float(request.form['amount'])
        recipient = request.form['recipient']
        conn = get_db_connection()
        sender = conn.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
        recipient_user = conn.execute('SELECT * FROM users WHERE username=?', (recipient,)).fetchone()

        if recipient_user and sender['balance'] >= amount:
            conn.execute('UPDATE users SET balance = balance - ? WHERE id=?', (amount, sender['id']))
            conn.execute('UPDATE users SET balance = balance + ? WHERE id=?', (amount, recipient_user['id']))
            conn.execute('INSERT INTO transactions (sender_id, receiver_id, amount) VALUES (?, ?, ?)',
                         (sender['id'], recipient_user['id'], amount))
            conn.commit()
        conn.close()
        return redirect('/dashboard')
    return render_template('send_money.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
