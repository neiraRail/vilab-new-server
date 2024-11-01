import socket
import signal
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
    try:
        while not disconnect:
            # Receive data from the client
            try:
                recieved_data = client_socket.recv(BUFFER_SIZE)
                if not recieved_data:
                    disconnect = True
                    continue
                
                data += recieved_data
                intentos = 0
            except socket.timeout as e:
                intentos += 1
                if intentos > 5:
                    disconnect = True
                    print("Se desconecta por timeout")
                continue

            
            while len(data) >= PACKET_LENGTH:
                packet = data[:PACKET_LENGTH]
                data = data[PACKET_LENGTH:]

                if packet[0:5] == b'SSSSS':
                    print("Notificación de apagado recibida del cliente.")
                    saver.send_buffer()
                    break

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
        saver.send_buffer()
    except db.SaveException as e:
        print(f"Ocurrió un error al enviar el buffer: {e}")
    except BaseException as e:
        print(f"Otro error ha ocurrido: {e}")
    finally:
        # Cierre ordenado de recursos
        client_socket.close()
        saver.close()
        print(f"Conexión cerrada para {client_address[0]}:{client_address[1]}")



def start_server(host, port):    
    # Crear socket de servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    shutdown = threading.Event()

    def signal_handler(sig, frame):
        print("\nRecibido SIGINT, cerrando el servidor...")
        shutdown.set()

    # Captura de señal para cierre ordenado
    signal.signal(signal.SIGINT, signal_handler)

    try:
        while not shutdown.is_set():
            try:
                client_socket, client_address = server_socket.accept()
                thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                thread.daemon = True
                thread.start()
            except socket.error as e:
                if shutdown.is_set():
                    break  # Salir del bucle si el servidor está en proceso de cierre
                print(f"Error al aceptar conexión: {e}")
    
    finally:
        # Cerrar el socket del servidor al finalizar
        server_socket.close()
        print("Servidor cerrado")

# Start the server
start_server('0.0.0.0', 8081)
