import os
import signal
import socket
import sys
import threading
import time

FILE_DIR = "/save"

def handleConnection(client_socket, connection_id):
    received_data = b""
    file_path = os.path.join(FILE_DIR, f"{connection_id}.file")

    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            received_data += data
            # Reset the timeout timer
            start_time = time.time()

        if len(received_data) > 0:
            with open(file_path, "wb") as file:
                file.write(received_data)        
        else:
            open(file_path, "w").close()  # Create an empty file

        client_socket.close()
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        client_socket.close()


def handleSignal(signum, frame):
    sys.exit(0)


def startServer(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(10)  # Maximum of 10 simultaneous connections

    # Set up signal handlers
    signal.signal(signal.SIGQUIT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    connection_id = 0

    while True:
        try:
            client_socket, address = server_socket.accept()

            connection_id += 1
            thread = threading.Thread(target=handle_connection, args=(client_socket, connection_id))
            thread.start()
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

    os.makedirs(FILE_DIR, exist_ok=True)

    start_server(port)
