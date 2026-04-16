import time
import subprocess
import sys
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SYNC_DIRS = ["/var/www/mi-aplicacion", "/opt/otra-carpeta"]
BROADCAST_PORT = 5000
EXCLUDE_PATTERNS = ["*.log", "*.tmp", "*.pyc", "__pycache__/", ".cache/", "tmp/"]
RSYNC_OPTIONS = ["-avz", "--delete", "--quiet"]

SLAVE_IPS = set()

def discover_slaves():
    global SLAVE_IPS
    SLAVE_IPS.clear()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(2)
        s.sendto(b"SLAVE_DISCOVER", ('<broadcast>', BROADCAST_PORT))
        while True:
            try:
                data, addr = s.recvfrom(1024)
                if data == b"SLAVE_RESPONSE":
                    if addr[0] != socket.gethostbyname(socket.gethostname()):
                        SLAVE_IPS.add(addr[0])
            except socket.timeout:
                break
    except:
        pass
    finally:
        s.close()
    print(f"Slaves detectados: {list(SLAVE_IPS) or 'Ninguno'}")

class SyncHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_sync = 0
        self.cooldown = 1.0

    def on_any_event(self, event):
        if event.is_directory:
            return
        if time.time() - self.last_sync < self.cooldown:
            return
        print(f"[SYNC] Cambio detectado → {event.event_type}: {event.src_path}")
        self.sync_to_all_slaves()
        self.last_sync = time.time()

    def sync_to_all_slaves(self):
        if not SLAVE_IPS:
            print("[SYNC] No hay slaves detectados")
            return
        exclude_args = [f"--exclude={p}" for p in EXCLUDE_PATTERNS]
        for ip in list(SLAVE_IPS):
            try:
                for directory in SYNC_DIRS:
                    cmd = [
                        "rsync", *RSYNC_OPTIONS, *exclude_args,
                        "-e", "ssh -o StrictHostKeyChecking=no -o BatchMode=yes",
                        f"{directory}/",
                        f"{ip}:{directory}/"
                    ]
                    subprocess.run(cmd, check=True, timeout=60)
                    print(f"[SYNC] Sincronizado {directory} a {ip}")
            except Exception as e:
                print(f"[ERROR] Fallo con {ip}: {e}")

def initial_sync():
    discover_slaves()
    print("Realizando sincronización inicial...")
    SyncHandler().sync_to_all_slaves()
    print("Sincronización completada.")

def start_realtime():
    discover_slaves()
    print(f"Iniciando clonación instantánea en {SYNC_DIRS}")
    print("   (Ctrl+C para detener)\n")
    event_handler = SyncHandler()
    observer = Observer()
    for directory in SYNC_DIRS:
        observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo...")
    finally:
        observer.stop()
        observer.join()

def start_slave_responder():
    print("Iniciando respuesta de broadcast como slave...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', BROADCAST_PORT))
    while True:
        data, addr = s.recvfrom(1024)
        if data == b"SLAVE_DISCOVER":
            s.sendto(b"SLAVE_RESPONSE", addr)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            initial_sync()
        elif sys.argv[1] == "start":
            start_realtime()
        elif sys.argv[1] == "slave":
            start_slave_responder()
        else:
            print("Uso:")
            print("  python3 instant_sync.py init     → Sincronización inicial")
            print("  python3 instant_sync.py start    → Modo tiempo real (master)")
            print("  python3 instant_sync.py slave    → Iniciar responder (en slaves)")
    else:
        print("Uso:")
        print("  python3 instant_sync.py init     → Sincronización inicial")
        print("  python3 instant_sync.py start    → Modo tiempo real (master)")
        print("  python3 instant_sync.py slave    → Iniciar responder (en slaves)")