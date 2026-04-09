#!/usr/bin/env python3

import time
import subprocess #Importaciones
import sys
from watchdog.observers import Observer #Fragmento observador
from watchdog.events import FileSystemEventHandler #Gestiona eventos

# Ajustes
SYNC_DIR = "/var/www/mi-aplicacion"                    # Cambia por tu directorio real
SLAVE_IPS = ["", ""]           # ¡¡¡¡¡¡¡AÑADIR DIRECCIONES IP ESCLAVAS!!!!!!! ¡¡¡¡¡¡¡POR AHORA EN BLANCO!!!!!!!
SSH_USER = "root"
EXCLUDE_PATTERNS = [
    "*.log", "*.tmp", "*.pyc", "__pycache__/",
    ".cache/", "tmp/", "*.swp", ".git/", ".env"
]

RSYNC_OPTIONS = ["-avz", "--delete", "--quiet"]  #Opciones de resincronización

class SyncHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_sync = 0
        self.cooldown = 1.0

    def on_any_event(self, event):
        if event.is_directory:
            return
        current_time = time.time()
        if current_time - self.last_sync < self.cooldown:
            return

        print(f"[SYNC] Cambio detectado → {event.event_type}: {event.src_path}") #Mensaje a imprimir si hay cambios
        self.sync_to_all_slaves()
        self.last_sync = current_time

    def sync_to_all_slaves(self):
        exclude_args = [f"--exclude={p}" for p in EXCLUDE_PATTERNS]
        for ip in SLAVE_IPS:
            try:
                cmd = [ #Ejecuta en CMD
                    "rsync", *RSYNC_OPTIONS, *exclude_args,
                    "-e", f"ssh -o StrictHostKeyChecking=no -o BatchMode=yes",
                    f"{SYNC_DIR}/",
                    f"{SSH_USER}@{ip}:{SYNC_DIR}/"
                ]
                subprocess.run(cmd, check=True, timeout=60) #Subproceso de verificación de sincronización
                print(f"[SYNC] Sincronizado a {ip}")
            except Exception as e:
                print(f"[ERROR] Fallo con {ip}: {e}")


def initial_sync(): #Sincronización inicial
    print("Realizando sincronización inicial...")
    SyncHandler().sync_to_all_slaves()
    print("Sincronización inicial completada.")


def start_realtime(): #Realmente la clonación instantánea
    print(f" Iniciando clonación instantánea en {SYNC_DIR}")
    print(f" Destinos: {', '.join(SLAVE_IPS)}")
    print(" (Ctrl+C para detener)\n")

    event_handler = SyncHandler()
    observer = Observer()
    observer.schedule(event_handler, SYNC_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n Deteniendo sincronización...")
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
        print("  python3 instant_sync.py init    → Sincronización inicial")
        print("  python3 instant_sync.py start   → Modo tiempo real")
