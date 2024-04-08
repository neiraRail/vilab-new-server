import socket
from utils.rtp import parseBytes
from utils.db import Saver
from utils.reloj import Reloj

BUFFER_SIZE = 1160
DELIMITER = b'\n\n'


def start_server(host, port):
    # Crear objeto Saver con conexión a base de datos
    saver = Saver()

    # Crear un socket UDP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enlazar el socket a una dirección y puerto específicos
    server_socket.bind((host, port))

    print(f"Server listening on {host}:{port}")

    # reloj = Reloj()

    while True:
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        print(f"Received data from {client_address[0]}:{client_address[1]}")

        if not data:
            continue


        # Manejo del delimitador
        packets = data.split(DELIMITER)
        for packet in packets[:-1]:
            try:
                unpacked_data = parseBytes(packet)
                saver.save(unpacked_data)
            except Exception as e:
                # Manejar excepciones
                print(e)

    # No se cierra el socket en UDP, ya que no hay conexión establecida

# Iniciar el servidor UDP
start_server('0.0.0.0', 8081)
