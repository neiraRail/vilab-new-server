import socket
import threading
import utils.rtp as rtp
import utils.db as db


PACKET_LENGTH = 58
BUFFER_SIZE = 1024
DELIMITER = b'\n\n'


def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    client_socket.settimeout(60)

    data = b''
    try:
        saver = db.Saver()
    except db.InitException as e:
        print(f"Ocurrió un error de init: {e}")
        client_socket.close()
        return
    except BaseException as e:
        print(f"Otro error ha ocurrido: {e}")
        client_socket.close()
        return

    disconnect = False
    intentos = 0
    while not disconnect:
        intentos += 1
        # Receive data from the client
        try:
            recieved_data = client_socket.recv(BUFFER_SIZE)
        except socket.timeout as e:
            if intentos > 5:
                disconnect = True
                print("Se desconecta por timeout")
            continue

        if not recieved_data:
            disconnect = True
            continue
        
        data += recieved_data
        while len(data) >= PACKET_LENGTH:
            packet = data[:PACKET_LENGTH]
            data = data[PACKET_LENGTH:]

            if packet[-2:] == DELIMITER:
                try:
                    unpacked_data = rtp.parseBytes(packet[:-2])
                    saver.save(unpacked_data)
                except rtp.ParseException as e:
                    print(f"Ocurrió un error de parseo: {e}")
                    disconnect = True
                    break
                except db.SaveException as e:
                    print(f"Ocurrió de guardado: {e}")
                    disconnect = True
                    break
                except BaseException as e:
                    print(f"Un error extraño ocurrió: {e}")
                    disconnect = True
                    break
            else:
                print("Datos invalidos")
                disconnect = True
                break
    
    # Force send whats left in the buffer
    try:
        saver.send_buffer()
    except db.SaveException as e:
        print(f"Ocurrió un error al enviar el buffer: {e}")
    except BaseException as e:
        print(f"Otro error ha ocurrido: {e}")
    
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

        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.daemon = True
        thread.start()


        
        

    # Close the server socket
    server_socket.close()

# Start the server
start_server('0.0.0.0', 8081)
