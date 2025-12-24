# backend/opc_connector.py
import json
import socket
import os

# Konfigurasi koneksi ke server OPC palsu
OPC_HOST = '127.0.0.1'
OPC_PORT = 65432

# --- PERBAIKAN PATH ---
# Dapatkan lokasi absolut dari file ini (opc_connector.py)
# Lalu bangun path ke file data dari sana. Ini lebih andal.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) # Naik satu level dari /backend ke /industrial_dashboard
DATA_FILE_PATH = os.path.join(ROOT_DIR, 'mock_opc_server', 'sensor_data.json')

def read_data():
    """
    Membaca data terkini dari file yang dibuat oleh server OPC palsu.
    Fungsi ini adalah satu-satunya tempat untuk logika pembacaan data.
    """
    try:
        # Gunakan path absolut yang sudah kita buat
        with open(DATA_FILE_PATH, 'r') as f:
            data = json.load(f)
            print(f"[OPC CONNECTOR] Berhasil membaca data: {data}")
            return data
    except FileNotFoundError:
        print(f"[OPC CONNECTOR] ERROR: File '{DATA_FILE_PATH}' tidak ditemukan. Pastikan server OPC berjalan.")
        # Kembalikan data kosong jika file tidak ada, agar tidak error
        return {"temperature": 0, "pressure": 0, "pump_status": "ERROR"}
    except json.JSONDecodeError:
        print(f"[OPC CONNECTOR] ERROR: File '{DATA_FILE_PATH}' rusak atau kosong.")
        return {"temperature": 0, "pressure": 0, "pump_status": "ERROR"}
    except Exception as e:
        print(f"[OPC CONNECTOR] ERROR: Gagal membaca data - {e}")
        return {"temperature": 0, "pressure": 0, "pump_status": "ERROR"}

def send_command(command):
    """
    Mengirim perintah ke server OPC melalui socket.
    Fungsi ini adalah satu-satunya tempat untuk logika pengiriman perintah.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((OPC_HOST, OPC_PORT))
            s.sendall(command.encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            print(f"[OPC CONNECTOR] Perintah '{command}' terkirim. Respon: '{response}'")
            return response
    except ConnectionRefusedError:
        print(f"[OPC CONNECTOR] ERROR: Tidak dapat terhubung ke server OPC di {OPC_HOST}:{OPC_PORT}")
        return "CONNECTION_ERROR"
    except Exception as e:
        print(f"[OPC CONNECTOR] ERROR: {e}")
        return "ERROR"