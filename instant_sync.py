#!/usr/bin/env python3

import time #Esta sección es de importaciones
import subprocess
import sys
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SYNC_DIR = "/var/www/mi-aplicacion"
SSH_USER = "root"
BROADCAST_PORT = 5000
EXCLUDE_PATTERNS = ["*.log", "*.tmp", "*.pyc", "__pycache__/", ".cache/", "tmp/"]

RSYNC_OPTIONS = ["-avz", "--delete", "--quiet"]

SLAVE_IPS = set()

def discover_slaves():
    global SLAVE_IPS
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(2)

        message = b"SLAVE_DISCOVER"
        s.sendto(message, ('<broadcast>', BROADCAST_PORT))

        while True:
            try:
                data, addr = s.recvfrom(1024)
                if data == b"SLAVE_RESPONSE" and addr[0] != socket.gethostbyname(socket.gethostname()):
                    SLAVE_IPS.add(addr[0])
            except socket.timeout:
                break
    except:
        pass
    finally:
        s.close()

    print(f"Slaves detectados por broadcast: {list(SLAVE_IPS) or 'Ninguno'}") #Msg detección 

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
            print("[SYNC] No se han detectado esclavos")
            return

        exclude_args = [f"--exclude={p}" for p in EXCLUDE_PATTERNS]
        for ip in list(SLAVE_IPS):
            try:
                cmd = [
                    "rsync", *RSYNC_OPTIONS, *exclude_args,
                    "-e", f"ssh -o StrictHostKeyChecking=no -o BatchMode=yes",
                    f"{SYNC_DIR}/",
                    f"{SSH_USER}@{ip}:{SYNC_DIR}/"
                ]
                subprocess.run(cmd, check=True, timeout=60)
                print(f" Sincronizado a {ip}")
            except Exception as e:
                print(f" Fallo con {ip}: {e}")


def initial_sync():
    discover_slaves()
    print("Realizando sincronización inicial...")
    SyncHandler().sync_to_all_slaves()
    print("Inicial completada.")


def start_realtime():
    discover_slaves()
    print(f" Iniciando clonación instantánea en {SYNC_DIR} (broadcast activado)")
    print(" (Utiliza CTRL+C para detener)\n")

    event_handler = SyncHandler()
    observer = Observer()
    observer.schedule(event_handler, SYNC_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo...")
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        initial_sync()
    elif len(sys.argv) > 1 and sys.argv[1] == "start":
        start_realtime()
    else:
        print("Uso:")
        print("  python3 instant_sync.py init    → Sincronización inicial + broadcast")
        print("  python3 instant_sync.py start   → Modo tiempo real con broadcast")