import signal
import socket
import sys

def handle_connection(client_socket):
    # Process the client connection
    data = client_socket.recv(4096)
    if not data:
        sys.stderr.write("ERROR: No data received\n")
    else:
        client_socket.sendall(data)
    
    client_socket.close()

def handle_signal(signum, frame):
    # Handle  SIGINT signals
    sys.exit(0)

def start_server(port):
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
            handle_connection(client_socket)
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
