import socket
import time
import utils.rtp as rtp
from utils.db import Saver


def start_server(host, port):
    # Crear objeto Saver con conexión a base de datos
    saver = Saver()
    
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
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

        clock = time.time_ns()
        packet_ps = 0
        data = b''
        size = 56

        disconnect = False
        while not disconnect:
            
            # Receive data from the client
            data += client_socket.recv(1024)
            print("Data received: ", len(data))
            
            counter = 0
            print("counter+size = "+str(counter+size))

            if len(data) < size:
                disconnect = True
                continue

            while counter+size <= len(data):
                
                if time.time_ns() - clock > 100000000:
                    print("Packet per second: ", packet_ps)
                    packet_ps = 0
                    clock = time.time_ns()
                
                # print("Unpacking from byte ", counter, " to ", counter+size)

                try:
                    unpacked_data = rtp.parseBytes(data[counter:counter+size])
                    saver.save(unpacked_data)
                    time.sleep(0.5)
                    packet_ps += 1
                except ValueError:
                    size += 1
                    continue
                except Exception as e:
                    print(e)
                    disconnect = True
                    shutdown = True
                    break
                counter += size
            
            data = data[counter:]
            print("Rest of the data: ", len(data))



    # Close the client connection
    client_socket.close()

    # Close the server socket
    server_socket.close()

# Start the server
start_server('localhost', 8080)
