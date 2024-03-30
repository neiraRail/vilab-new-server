import socket
import threading
import utils.rtp as rtp
from utils.db import Saver
from utils.reloj import Reloj


BUFFER_SIZE = 1024
DELIMITER = b'\n\n'


def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    client_socket.settimeout(10)

    data = b''
    saver = Saver()
    reloj = Reloj()

    disconnect = False
    while not disconnect:
        # Receive data from the client
        try:
            recieved_data = client_socket.recv(BUFFER_SIZE)
        except socket.timeout as e:
            print("Timeout")
            disconnect = True
            continue

        if not recieved_data:
            disconnect = True
            continue
        
        data += recieved_data
        # print("Data received: ", len(data))
        # reloj.mostrarFrecuencia()
        while DELIMITER in data:
            packet, data = data.split(DELIMITER, 1)
            try:
                unpacked_data = rtp.parseBytes(packet)
                saver.save(unpacked_data)
                reloj.aumentarContador()
            except Exception as e:
                # TODO: Add error handling, separate types of exceptions, at least in parse exceptions and save exceptions
                print(e)
                disconnect = True
                break

    # Close the client connection
    client_socket.close()



def start_server(host, port):    
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_socket.bind((host, port))

    # Listen for incoming connections
    server_socket.listen(1)

    shutdown = False
    while not shutdown:
        print(f"Server listening on {host}:{port}")

        # Accept a client connection
        client_socket, client_address = server_socket.accept()

        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
        
        

    # Close the server socket
    server_socket.close()

# Start the server
start_server('0.0.0.0', 8080)
