import socket
import sys
import signal
import threading

def handle_connection(client_socket):
    data = client_socket.recv(4096)
    if not data:
        sys.stderr.write("ERROR: No data received\n")
    else:
        # Send the desired message back to the client
        message = "accio (0/5)"
        client_socket.sendall(message.encode())
    
    client_socket.close()

def handle_signal(signum, frame):
    sys.exit(0)

def start_server(port):
    if not (0 <= port <= 65535):
        sys.stderr.write("ERROR: Invalid port number (0-65535)\n")
        sys.exit(1)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(10)

    # Set up signal handlers
    signal.signal(signal.SIGQUIT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    while True:
        try:
            client_socket, address = server_socket.accept()

            # Create a new thread to handle each client
            client_thread = threading.Thread(target=handle_connection, args=(client_socket,))
            client_thread.start()
        except KeyboardInterrupt:
            break

    server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("ERROR: Port number not provided\n")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number\n")
        sys.exit(1)

    start_server(port)
