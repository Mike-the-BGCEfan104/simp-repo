# Mike's Repository
Proyecto para el Trabajo de Fin de Grado (TFG)

Este repositorio contiene la configuración y los scripts necesarios para el despliegue de un servidor automatizado. Está diseñado bajo el principio de **Self-Contained Repo**, facilitando la clonación y replicación idéntica entre distintos entornos de servidor.


## Despliegue y Clonación Rápida

Este proyecto utiliza un script de orquestación en Python para asegurar la réplica correcta de la configuración, gestionando permisos y variables de entorno de forma automática.

### 1. Requisitos Previos
Antes de comenzar, se deben tener instalados los siguientes paquetes en el servidor Linux:
* `git`
* `python3`

### 2. Instalación Automática
Se ejecuta el siguiente comando para descargar el script de configuración y desplegar el entorno completo en un solo paso:

```bash
curl -O [https://raw.githubusercontent.com/Mike-the-BGCEfan104/simp-repo/main/self-cont.py](https://raw.githubusercontent.com/Mike-the-BGCEfan104/simp-repo/main/self-cont.py) && python3 self-cont.py
