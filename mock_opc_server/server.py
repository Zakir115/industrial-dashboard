# mock_opc_server/server.py
import time
import socket
import threading
import random
import json # <--- TAMBAHKAN IMPORT INI

# --- Konfigurasi Server Palsu ---
HOST = '127.0.0.1'
PORT = 65432
# ---------------------------------

# Data sensor yang akan disimulasikan
sensor_data = {
    "temperature": 25.0,
    "pressure": 1.0,
    "pump_status": "OFF"
}

def update_sensor_data():
    """Fungsi untuk mengubah data sensor secara acak dan menuliskannya ke file."""
    while True:
        # Simulasi perubahan data
        sensor_data["temperature"] += random.uniform(-1, 1)
        sensor_data["pressure"] += random.uniform(-0.05, 0.05)
        
        # Pastikan nilai tetap dalam batas wajar
        sensor_data["temperature"] = max(20, min(30, sensor_data["temperature"]))
        sensor_data["pressure"] = max(0.8, min(1.2, sensor_data["pressure"]))
        
        # <--- TAMBAHKAN BAGIAN INI ---
        # Tulis data terbaru ke file JSON
        try:
            with open('sensor_data.json', 'w') as f:
                json.dump(sensor_data, f)
            print(f"[OPC SERVER] Data diperbarui dan ditulis ke file: {sensor_data}")
        except Exception as e:
            print(f"[OPC SERVER] Gagal menulis file: {e}")
        # --- AKHIR TAMBAHAN ---
        
        time.sleep(3)

def handle_client_connection(conn, addr):
    """Menangani koneksi dari client (dashboard backend) untuk menerima perintah."""
    print(f"[OPC SERVER] Terhubung dengan {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            command = data.decode('utf-8')
            print(f"[OPC SERVER] Menerima perintah: {command}")
            
            if command == "START_PUMP":
                sensor_data["pump_status"] = "ON"
                conn.sendall("PUMP_STARTED".encode('utf-8'))
            elif command == "STOP_PUMP":
                sensor_data["pump_status"] = "OFF"
                conn.sendall("PUMP_STOPPED".encode('utf-8'))
            else:
                conn.sendall("UNKNOWN_COMMAND".encode('utf-8'))
    print(f"[OPC SERVER] Koneksi dengan {addr} ditutup.")

def start_opc_server():
    """Fungsi utama untuk menjalankan server OPC palsu."""
    print("[OPC SERVER] Menjalankan server...")
    
    # Jalankan thread untuk memperbarui data sensor
    sensor_thread = threading.Thread(target=update_sensor_data, daemon=True)
    sensor_thread.start()
    
    # Jalankan server socket untuk menerima perintah
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[OPC SERVER] Mendengarkan perintah di {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_opc_server()