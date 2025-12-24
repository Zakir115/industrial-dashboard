# backend/app.py
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO
import logging

# Impor modul-modul kita
import opc_connector

# --- Konfigurasi Aplikasi ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'rahasia_sangat_aman'
socketio = SocketIO(app, async_mode='eventlet')

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Background Task untuk membaca data OPC (tidak berubah) ---
def background_task():
    print("Background task untuk membaca data OPC telah dimulai.")
    while True:
        data = opc_connector.read_data()
        socketio.emit('opc_data_update', data)
        socketio.sleep(3)

# --- Event Handler untuk WebSocket ---
@socketio.on('connect')
def handle_connect():
    print('Client terhubung ke WebSocket.')
    if not hasattr(socketio, 'background_thread_started'):
        socketio.background_thread_started = True
        socketio.start_background_task(background_task)
        print("Background task dimulai.")
    initial_data = opc_connector.read_data()
    socketio.emit('opc_data_update', initial_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client terputus dari WebSocket.')

# --- EVENT HANDLER UNTUK KONTROL (BARU) ---
@socketio.on('control_command')
def handle_control_command(json):
    """
    Fungsi ini dijalankan saat client mengirim event 'control_command'.
    """
    command = json['command']
    print(f"Menerima perintah kontrol dari client: {command}")
    
    # Panggil fungsi send_command dari opc_connector untuk mengirim perintah ke server OPC
    response = opc_connector.send_command(command)
    
    # Kirim balik respon ke client yang mengirim perintah
    socketio.emit('command_response', {'status': response})

# --- Rute Utama Aplikasi (tidak berubah) ---
@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Username atau password salah')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- Menjalankan Aplikasi (tidak berubah) ---
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)