import socket # for socket programming
import threading # for each connection thread
import sys
from server import start_server


# --- GLOBALS ----
_CONNECTIONS = {}
_NEW_ID = 1
_SERVER_SOCKET = None
_LISTENING_PORT = None
_MY_IP = None


"""
Display available commands and their usage
"""
def handle_help():
    print("Available commands:")
    print("  myip                : Display the IP address of this device")
    print("  myport              : Display the port number this process runs on")
    print("  connect <ip> <port> : Establish a new TCP connection to the given destination")
    print("  list                : Display all active connections")
    print("  terminate <id>      : Terminate connection according to the list index")
    print("  send <id> <message> : Send a message to the host on the specified connection")
    print("  exit                : Close all connections and terminate this process")


def handle_myip():
    print(f"The IP address is {_MY_IP}")


def handle_myport():
    print(f"The program runs on port number {_LISTENING_PORT}")


def handle_connect(ip, port):
    global _CONNECTIONS
    global _NEW_ID

    if ip == _MY_IP:
        print("CANNOT CONNECT TO SELF")
        return
        
    for (current_ip, port, socket) in _CONNECTIONS.values():
        if ip == current_ip:
            print("CANNOT CONNECT TO DUPLICATE")
            return
  
    s = socket.socket()
    s.connect((ip, int(port)))
    _CONNECTIONS[_NEW_ID] = (ip, port, s)
    _NEW_ID += 1


"""
Print out all IP addresses and portnumbers in list
"""
def handle_list():
    global _CONNECTIONS
    
    for id, pair in _CONNECTIONS.items():
        print(f"ID: {id}, IP address: {pair[0]}, Port Number: {pair[1]}")


"""
Terminate a connection if it exists in the global dictionary
"""
def handle_terminate(id):
    global _CONNECTIONS

    if id in _CONNECTIONS:
        ip, _, s = _CONNECTIONS[id]
        s.close()
        del _CONNECTIONS[id]
    else:
        print(f"ERROR: ID not in active _CONNECTIONS")


def handle_send(id, message):
    global _CONNECTIONS

    server_ip = _CONNECTIONS[i][0]
    server_port = _CONNECTIONS[i][1]
    server_socket = _CONNECTIONS[i][2]

    server_socket.send(message.encode())

    


def handle_exit():
    global _CONNECTIONS
    global _SERVER_SOCKET

    for connection in _CONNECTIONS.values():
        connection[2].close()
    _CONNECTIONS.clear()

    _SERVER_SOCKET.close()
    

def main():
    global _MY_IP
    global _SERVER_SOCKET
    global _LISTENING_PORT
    
    # Minimal command-line port handling
    if len(sys.argv) != 2:
        print("Usage: python3 chat.py <port>")
        sys.exit(1)
    try:
        _LISTENING_PORT = int(sys.argv[1])
    except ValueError:
        print("Port must be an integer.")
        sys.exit(1)

    # Start the server and save the socket
    _SERVER_SOCKET = start_server(_LISTENING_PORT)

    try:
        ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip.connect(("8.8.8.8", 80))
        _MY_IP = ip.getsockname()[0]
        ip.close()
    except Exception as e:
        print(f"Could not determine local IP address: {e}")

    while True:
        message = input(">>")
        message = message.strip()
        message_parts = message.split(" ")
        command = message_parts[0].lower()

        match command:
            case "help":
                handle_help()
            case "myip":
                handle_myip()
            case "myport":
                handle_myport()
            case "connect":
                handle_connect(message_parts[1], message_parts[2])
            case "list":
                handle_list()
            case "terminate":
                handle_terminate(message_parts[1])
            case "send":
                handle_send(message_parts[1], message_parts[2])
            case "exit":
                handle_exit()
            case _:
                print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()