import socket
import sys
import time

# Function to check hostname
def check_hostname(sock, hostname):
    try:
        # Use gethostbyname to get the IP address of the given hostname
        _, _, _ = socket.gethostbyname(hostname)
        print(f"{hostname} exists.")
    except socket.gaierror as e:
        if e.errno == socket.EAI_NONAME:
            handle_error(sock, f"{hostname} does not exist or is incorrect.")
        else:
            handle_error(sock, f"Error occurred while checking {hostname}: {e.strerror}")

def terminate_connection(sock):
    sock.close()
    sys.exit(1)

# Function to handle network or server errors
def handle_error(sock, error_message):
    sys.stderr.write("ERROR: " + error_message + "\n")
    terminate_connection(sock)

# Function to receive full command from the server
def receive_command(sock):
    command = b""
    while b"\r\n" not in command:
        try:
            data = sock.recv(1024)
            if not data:
                handle_error(sock, "Failed to read command from server.")
        except socket.timeout:
            handle_error(sock, "Timeout occurred while receiving command from server.")
        command += data
    return command

# Function to send confirmation to the server
def send_confirmation(sock):
    try:
        sock.sendall(b"confirm\r\n")
    except socket.timeout:
        handle_error(sock, "Timeout occurred while sending confirmation to server.")

# Function to send file to the server
def send_file(sock, file_path):
    try:
        # Add headers here before sending the file
        headers = "X-Custom-Header: Value\r\n"

        sock.sendall(headers.encode())

        with open(file_path, "rb") as file:
            while True:
                data = file.read(10000)
                if not data:
                    break
                try:
                    sock.send(data)
                except socket.timeout:
                    handle_error(sock, "Timeout occurred while sending file to server.")
                time.sleep(10)
        print(f"File '{file_path}' sent successfully")
       
    except FileNotFoundError:
        sys.stderr.write("ERROR: Specified file not found.\n")
        terminate_connection(sock)

# Main function
def main(server_host, server_port, file_path):

    # Create a socket and set timeout
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    # check hostname
    check_hostname(sock, server_host)

    try:
        # Connect to the server
        sock.connect((server_host, server_port))

        # Receive two full commands from the server
        for _ in range(2):
            command = receive_command(sock)
            if command != b"accio\r\n":
                handle_error(sock, "Received incorrect command from server.")
            send_confirmation(sock)

        # Send the file to the server
        send_file(sock, file_path)

    except socket.timeout:
        handle_error(sock, "Timeout occurred while connecting to server.")

    except socket.gaierror as e:
        handle_error(sock, f"Failed to connect to server: {e.strerror}")

    finally:
        # Terminate the connection
        terminate_connection(sock)


# Run the client command line 
if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.stderr.write("ERROR: Insufficient command line arguments.\n")
        sys.exit(1)
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    if server_port < 0 or server_port > 65535:
        sys.stderr.write("ERROR: invalid server port.\n")
        sys.exit(1)
    file_path = sys.argv[3]
    main(server_host, server_port, file_path)
