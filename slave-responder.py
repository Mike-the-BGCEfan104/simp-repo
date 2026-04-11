#!/usr/bin/env python3
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 5000))

print("Escuchando broadcast como esclavo...")
while True:
    data, addr = s.recvfrom(1024)
    if data == b"SLAVE_DISCOVER":
        s.sendto(b"SLAVE_RESPONSE", addr)