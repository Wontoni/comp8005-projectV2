import socket
import struct
import pickle
import subprocess

server = None
server_host = "::"
server_port = 8080

def main():
    try:
        create_socket()
        bind_socket()
        while True:
            conn, address = accept_connection()
            try:
                data = receive_data(conn)
                output = run_command(data)
                send_message(conn, output)
            finally:
                conn.close()
    except KeyboardInterrupt:
        print("\nServer interrupted by user. Exiting...")
        cleanup(True)
    except Exception as e:
        handle_error(f"Unexpected error occurred: {e}")
    finally:
        cleanup(False)

def run_command(command):
    try:
        result = subprocess.run(command.split(' '), text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return result
    except FileNotFoundError as e:
        return e
    except subprocess.SubprocessError as e:
        return e

def create_socket():
    try:
        global server
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Server is running...")
    except Exception as e:
        handle_error(f"Failed to create socket server: {e}")

def bind_socket():
    try:
        addr = (server_host, server_port)
        server.bind(addr)
        server.listen(5)
        print('Server binded and waiting for incoming connections...')
    except Exception as e:
        handle_error(f"Failed to bind to the server: {e}")

def accept_connection():
    try:
        conn, address = server.accept()
        print("Accepted connection from", address)
        return conn, address
    except Exception as e:
        handle_error(f"Failed to accept connection: {e}")

def receive_data(conn):
    try:
        # Read the size of the incoming data
        data_size = conn.recv(4)
        if not data_size:
            handle_error("No data size received")

        data_size = struct.unpack(">I", data_size)[0]
        received_data = b""

        while len(received_data) < data_size:
            chunk = conn.recv(data_size - len(received_data))
            if not chunk:
                handle_error("Connection closed by client")
            received_data += chunk

        data = pickle.loads(received_data)
        return data
    except Exception as e:
        handle_error(f"Failed to receive data: {e}")

def send_message(conn, words):
    try:
        encoded = pickle.dumps(words)
        conn.sendall(struct.pack(">I", len(encoded)))
        conn.sendall(encoded)
    except Exception as e:
        handle_error(f"Failed to send message: {e}")

def handle_error(err_message):
    print(f"Error: {err_message}")
    cleanup(False)

def cleanup(success):
    if server:
        server.close()
    if success:
        exit(0)
    exit(1)

main()