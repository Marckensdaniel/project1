import socket
import sys
import errno

# Function to check hostname
def checkHostname(sock, hostname):
    try:
        # Use gethostbyname_ex to get the IP address of the given hostname
        _, _, _ = socket.gethostbyname_ex(hostname)
        print(f"{hostname} exists.")
    except socket.gaierror as e:
        if e.errno == socket.EAI_NONAME:
            handleError(sock, f"{hostname} does not exist or is incorrect.")
        else:
            handleError(sock, f"Error occurred while checking {hostname}: {e.strerror}")

# Function to gracefully terminate the connection
def terminateConnection(sock):
    sock.close()
    sys.exit(1)

# Function to handle network
def handleError(sock, error_message):
    sys.stderr.write("ERROR: " + error_message + "\n")
    terminateConnection(sock)

# Function to receive full command from the server
def receiveCommand(sock):
    command = b""
    while b"\r\n" not in command:
        try:
            data = sock.recv(1024)
            if not data:
                handleError(sock, "Failed to read command from server.")
        except socket.timeout:
            handleError(sock, "Timeout occurred while receiving command from server.")
        command += data
    return command

# Function to send confirmation to the server
def sendConfirmation(sock):
    try:
        sock.sendall(b"confirm\r\n")
    except socket.timeout:
        handleError(sock, "Timeout occurred while sending confirmation to server.")

# Function to send file to the server
def sendFile(sock, file_path):
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
                    sock.sendall(data)
                    
                    print(f"File '{file_path}' sent successfully")

                except socket.timeout:
                    handleError(sock, "Timeout occurred while sending file to server.")
    except FileNotFoundError:
        sys.stderr.write("ERROR: Specified file not found.\n")
        terminateConnection(sock)

# Main function
def main(server_host, server_port, file_path):

    # Create a socket and set timeout
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    # check hostname
    checkHostname(sock, server_host)

    try:
        # Connect to the server
        sock.connect((server_host, server_port))

        # Receive two full commands from the server
        for _ in range(2):
            command = receiveCommand(sock)
            if command != b"accio\r\n":
                handleError(sock, "Received incorrect command from server.")
            send_confirmation(sock)

        # Send the file to the server
        sendFile(sock, file_path)

    except socket.timeout:
        handleError(sock, "Timeout occurred while connecting to server.")

    except socket.gaierror as e:
        handleError(sock, f"Failed to connect to server: {e.strerror}")

    finally:
        # Terminate the connection
        terminateConnection(sock)

# Run the client with command line arguments
if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.stderr.write("ERROR: Insufficient command line arguments.\n")
        sys.exit(1)
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    file_path = sys.argv[3]
    main(server_host, server_port, file_path)
