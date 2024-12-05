import socket
import sys
import ipaddress
import struct
import pickle

# Variables to change based on server host location

# Change to ipv4 for connection via IPv4 Address or ipv6 for IPv6
server_port = 8080


command = None
server_host = None
client = None


def main():
    
    check_args(sys.argv)
    handle_args(sys.argv)
    create_socket()
    connect_client()
    send_message()
    receieve_response()

def check_args(args):
    try:
        if len(args) != 3:
            raise Exception("Invalid number of arguments")
        is_ipv4(args[1]) # Will handle invalid addresses
    except Exception as e:
        handle_error(e)
        exit(1)

def handle_args(args):
    global command, server_host
    try:
        command = sys.argv[2]
        server_host = sys.argv[1]
    except Exception as e:
        handle_error("Failed to retrieve inputted arguments.")

def create_socket():
    try: 
        global client
        client = socket.socket((socket.AF_INET6, socket.AF_INET)[is_ipv4(server_host)], socket.SOCK_STREAM)

    except Exception as e:
        handle_error("Failed to create client socket")

def connect_client():
    try: 
        client.settimeout(10)
        client.connect((server_host, server_port))
    except Exception as e:
        handle_error(f"Failed to connect to socket with the address and port - {server_host}:{server_port}")

def send_message(): 
    try: 
        global command
        encoded = pickle.dumps(command)
        client.sendall(struct.pack(">I", len(encoded)))
        client.sendall(encoded)
        
    except Exception as e:
        print(e)
        handle_error("Failed to send words")
        exit(1)

def receieve_response():
    try: 
        client.settimeout(10)
        data_size = struct.unpack(">I", client.recv(4))[0]
        # receive payload till received payload size is equal to data_size received
        received_data = b""
        remaining_size = data_size
        while remaining_size != 0:
            received_data += client.recv(remaining_size)
            remaining_size = data_size - len(received_data)
        decoded_response = pickle.loads(received_data)

        display_message(decoded_response)
    except Exception as e:
        handle_error("Failed to receive response from server")
        exit(1)


def is_ipv4(ip_str):
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except ipaddress.AddressValueError:
        pass

    try:
        ipaddress.IPv6Address(ip_str)
        return False
    except ipaddress.AddressValueError:
        pass
    err_message = "Invalid IP Address found."
    handle_error(err_message)
    
def handle_error(err_message):
    print(f"Error: {err_message}")
    cleanup(False)
    
def display_message(message):
    print('Received response')
    if message.stderr:
        print(message.stderr)
    elif message.stdout:
        print(message.stdout)
    else:
        print(message)
    cleanup(True)

def cleanup(success):
    if client:
        client.close()
    if success:
        exit(0)
    exit(1)

if __name__ == "__main__":
    main()