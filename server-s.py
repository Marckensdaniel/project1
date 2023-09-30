import signal
import socket
import sys

def handle_connection(client_socket,address):
     client_socket.settimeout(10)
     try:
        print(f"Client {address[0]}:{address[1]} connected")
        data = client_socket.recv(4096)
        #print(data)
        if not data:
             sys.stderr.write("ERROR: No data received\n")
        elif data != b'confirm-accio\r\n':
            sys.stderr.write("ERROR: Wrong Confirmation\n")
        else:
            client_socket.send(b'accio\r\n')
        

        data = client_socket.recv(4096)
          
        #print(data)
        if not data:
            sys.stderr.write("ERROR: No data received\n")
        elif data != b'confirm-accio-again\r\n':
            sys.stderr.write("ERROR: Wrong Confirmation\n")
        else:
            client_socket.send(b'accio\r\n')
        buffer = bytearray()
        while True:
             data = client_socket.recv(1024)
             if not data:
                break
             buffer.extend(data)
            
        num_bytes_received = len(buffer)
        print(f"Received {num_bytes_received} bytes")
        
     except socket.timeout:
            sys.stderr.write("ERROR: Timeout while waiting for data\n")
     except Exception as e:
            sys.stderr.write(f"ERROR: {str(e)}\n")
     finally:
            client_socket.close()

def handle_signal(signum, frame):
    # Handle SIGQUIT, SIGTERM, SIGINT signals
    sys.exit(0)

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(10)  # Maximum of 10 simultaneous connections
    
    # Set up signal handlers
    signal.signal(signal.SIGQUIT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    while True:
        try:
            client_socket, address = server_socket.accept()
            handle_connection(client_socket,address)
        except KeyboardInterrupt:
            break

    server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("ERROR: Port number not provided\n")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
        if port < 0 or port > 65535:
           sys.stderr.write("ERROR: Invalid port number\n")
           sys.exit(1)
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number\n")
        sys.exit(1)

    start_server(port)
