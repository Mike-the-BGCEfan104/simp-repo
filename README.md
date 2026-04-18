# Mike's Repository
Proyecto para el Trabajo de Fin de Grado (TFG)

Este repositorio contiene la configuración y los scripts necesarios para el despliegue de un servidor automatizado. Está diseñado bajo el principio de **Self-Contained Repo**, facilitando la clonación y replicación idéntica entre distintos entornos de servidor.


## Despliegue y Clonación Rápida

Este proyecto utiliza un script de orquestación en Python para asegurar la réplica correcta de la configuración, gestionando permisos y variables de entorno de forma automática.

### Requisitos previos
Antes de comenzar, se deben tener instalados los siguientes paquetes en el servidor Linux:
- git
- python3
- rsync (con obligatoriedad de tenerlo en servidor)
Instalación de dependencias: pip3 install -r requirements.txt
Uso de clonación instantánea:
- En el servidor master: python3 instant_sync.py init, python3 instant_sync.py start
- En cada servidor slave: python3 instant_sync.py slave (Se recomienda ejecutar el slave en background con screen o systemd)

### Instalación automática
Se ejecuta el siguiente comando para descargar el script de configuración y desplegar el entorno completo en un solo paso:

```bash
curl -O [https://raw.githubusercontent.com/Mike-the-BGCEfan104/simp-repo/main/self-cont.py](https://raw.githubusercontent.com/Mike-the-BGCEfan104/simp-repo/main/self-cont.py) && python3 self-cont.py

Instalación de dependencias:
pip3 install -r requirements.txt
Configuración inicial de SSH (una sola vez): en el servidor master ejecuta: ssh-keygen -t ed25519 y ssh-copy-id usuario_actual@IP_DEL_SLAVE
Repite ssh-copy-id para cada slave. Esto permite conexión sin contraseña.
Uso de clonación instantánea: en el servidor master: python3 instant_sync.py init y python3 instant_sync.py start
En cada servidor slave: python3 instant_sync.py slave (Se recomienda ejecutar el slave en background con screen o tmux)
