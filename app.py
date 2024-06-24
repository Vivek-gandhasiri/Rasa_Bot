import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
from multiprocessing import Process
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Initialize CORS extension
socketio = SocketIO(app)
# Database Initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS matches
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, game TEXT, team1 TEXT, team2 TEXT, date TEXT, bet1 REAL, bet2 REAL)''')
    conn.commit()
    conn.close()

init_db()

# Function to run Rasa server
def run_rasa_server():
    import subprocess
    subprocess.run(["rasa", "run", "-m", "models", "--enable-api"])

# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        game = request.form['game']
        team1 = request.form['team1']
        team2 = request.form['team2']
        date = request.form['date']
        bet1 = request.form['bet1']
        bet2 = request.form['bet2']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO matches (game, team1, team2, date, bet1, bet2) VALUES (?, ?, ?, ?, ?, ?)",
                  (game, team1, team2, date, bet1, bet2))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    return render_template('admin.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    conn.close()
    return 'Registration successful!'

@app.route('/home')
def home():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM matches")
    matches = c.fetchall()
    conn.close()
    return render_template('home.html', matches=matches)
@app.route('/chat')
def chat():
    return render_template('chat.html')

# SocketIO event handlers
@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    # Send the user message to the Rasa server
    response = requests.post("http://0.0.0.0:5005", json={"message": message})
    if response.status_code == 200:
        bot_response = response.json()
        emit('message', bot_response)


if __name__ == '__main__':
    # Start Rasa server in a separate process
    rasa_process = Process(target=run_rasa_server)
    rasa_process.start()

    # Start Flask app with SocketIO support
    socketio.run(app, debug=True)

    # Wait for Rasa process to finish
    rasa_process.join()
