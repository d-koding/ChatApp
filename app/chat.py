import socket
import threading
import sys


# --- GLOBALS ----
_CONNECTIONS = {}
_NEW_ID = 1
_SERVER_SOCKET = None
_LISTENING_PORT = None
_MY_IP = None


def handle_server_connection(connection_socket, address):
    """
    Handle messages from a connected peer.
    Prints received messages and listens for 'terminate' message.
    Automatically closes and removes the connection when done.
    """
    global _CONNECTIONS
    global _NEW_ID

    # Register if new
    if not any(sock == connection_socket for _, (_, _, sock) in _CONNECTIONS.items()):
        _CONNECTIONS[_NEW_ID] = (address[0], address[1], connection_socket)
        print(f"\nAdded incoming connection from {address[0]}:{address[1]} with ID {_NEW_ID}\n>> ", end="")
        _NEW_ID += 1

    try:
        while True:
            data = connection_socket.recv(1024)
            if not data:
                break

            message = data.decode().strip()

            if message.lower() == "terminate":
                print(f"\nPeer {address[0]} terminates the connection\n>> ", end="")
                break

            print(f'\nMessage received from {address[0]}: "{message}"\n>> ', end="")

    except Exception as e:
        print(f"Error with connection {address}: {e}")

    finally:
        try:
            connection_socket.close()
        except OSError:
            pass  # Socket may already be closed

        removed_id = None
        for cid, (ip, port, sock) in list(_CONNECTIONS.items()):
            if sock == connection_socket:
                removed_id = cid
                del _CONNECTIONS[cid]
                break


def start_server(port):
    """
    Start a server socket listening on the given port.
    Returns the socket so the main shell can access it.
    """
    global _CONNECTIONS
    global _NEW_ID

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", port))
    s.listen(10)
    print(f"Server listening on port {port}")

    # Run the accept loop in a background thread
    def accept_loop():
        global _CONNECTIONS
        global _NEW_ID

        while True:
            new_conn, new_addr = s.accept()
            new_ip, new_port = new_addr

            # Enforce max connection limit
            if len(_CONNECTIONS) >= 3:
                print(f"\nERROR: Max number of connections (3) reached. Rejecting connection from {new_ip}:{new_port}\n>> ", end="")
                new_conn.close()
                continue

            threading.Thread(target=handle_server_connection, args=(new_conn, new_addr), daemon=True).start()

            _CONNECTIONS[_NEW_ID] = (new_ip, new_port, new_conn)
            _NEW_ID += 1

    threading.Thread(target=accept_loop, daemon=True).start()

    return s

    
def handle_help():
    """
    Display the list of available commands and their usage.
    """
    print("Available commands:")
    print("  myip                : Display the IP address of this device")
    print("  myport              : Display the port number this process runs on")
    print("  connect <ip> <port> : Establish a new TCP connection to the given destination")
    print("  list                : Display all active connections")
    print("  terminate <id>      : Terminate connection according to the list index")
    print("  send <id> <message> : Send a message to the host on the specified connection")
    print("  exit                : Close all connections and terminate this process")


def handle_myip():
    """
    Display IP address of the local machine running the program.
    """
    print(f"The IP address is {_MY_IP}")


def handle_myport():
    """
    Display the port number on which the program is currently running.
    """
    print(f"The program runs on port number {_LISTENING_PORT}")


def handle_connect(dest_ip, dest_port):
    """
    Connect to a remote peer and register the connection.
    Prevents connecting to self or to an already connected peer.
    Also, adds the connection to _CONNECTIONS and starts a listener thread.
    """
    global _CONNECTIONS
    global _NEW_ID
    global _MY_IP
    global _LISTENING_PORT
    
    if len(_CONNECTIONS) >= 3:
        print("ERROR: Max number of connections (3) has been reached")
        return

    # Prevent self-connection
    if dest_ip == _MY_IP and int(dest_port) == _LISTENING_PORT:
        print(f"ERROR: Cannot connect to yourself on port {_LISTENING_PORT}")
        return

    for conn_id, (ip, port, _) in _CONNECTIONS.items():
        if ip == dest_ip and port == int(dest_port):
            print(f"ERROR: Already connected to {dest_ip}:{dest_port}")
            return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((dest_ip, int(dest_port)))

        # Add to connection list
        _CONNECTIONS[_NEW_ID] = (dest_ip, int(dest_port), sock)
        print(f"The connection to peer {dest_ip} is successfully established")

        # Start thread to listen for messages from this peer
        threading.Thread(
            target=handle_server_connection,
            args=(sock, (dest_ip, int(dest_port))),
            daemon=True
        ).start()

        _NEW_ID += 1

    except Exception as e:
        print(f"ERROR: Could not connect to {dest_ip}:{dest_port} ({e})")


def handle_list():
    """
    Display all active connections.
    Prints the connection ID, IP address, and port number for
    each currently connected peer.
    """
    global _CONNECTIONS
    
    print("id:    IP address       Port No.")
    for id, (ip, port, _) in _CONNECTIONS.items():
        print(f"{id:<5}  {ip:<15}  {port}")


def handle_send(conn_id, message):
    """
    Send a message to a connected peer using its connection ID.
    """
    global _CONNECTIONS
    conn_id = int(conn_id)

    if conn_id not in _CONNECTIONS:
        print(f"ERROR: Connection ID {conn_id} not found.")
        return

    ip, port, sock = _CONNECTIONS[conn_id]

    try:
        sock.send(message.encode())
        print(f"Message sent to {ip}:{port}: {message}")

    except Exception as e:
        print(f"ERROR: Could not send to {ip}:{port} ({e})")
        sock.close()
        del _CONNECTIONS[conn_id]


def handle_terminate(conn_id):
    """
    Terminates connection with a specified ID.
    Prints error if conn_id is not in active connection, 
    otherwise notifies peer of successful termination.
    """
    global _CONNECTIONS
    conn_id = int(conn_id)

    if conn_id not in _CONNECTIONS:
        print(f"[Error] ID {conn_id} not in active connections.")
        return

    ip, port, sock = _CONNECTIONS[conn_id]

    # Notify peer of termination
    try:
        sock.send("terminate".encode())
    except Exception as e:
        print(f"ERROR sending terminate message: {e}")
    
    # Remove from connection list (if not already deleted)
    if conn_id in _CONNECTIONS:
        del _CONNECTIONS[conn_id]


def handle_exit():
    """
    Quit the current program and terminate all connections.
    """
    global _CONNECTIONS
    global _SERVER_SOCKET

    for conn_id in list(_CONNECTIONS.keys()):
        try:
            handle_terminate(conn_id)
        except Exception as e:
            print(f"Error closing connection {conn_id}: {e}")

    _CONNECTIONS.clear()
    _SERVER_SOCKET.close()
    sys.exit(0)


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
        message = input(">> ").strip()
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
                if len(message_parts) < 3:
                    print("Usage: connect <ip> <port>")
                else:
                    handle_connect(message_parts[1], message_parts[2])
            case "list":
                handle_list()
            case "terminate":
                handle_terminate(message_parts[1])
            case "send":
                if len(message_parts) < 3:
                    print("Usage: send <id> <message>")
                else:
                    conn_id = message_parts[1]
                    msg = " ".join(message_parts[2:])
                    handle_send(conn_id, msg)
            case "exit":
                handle_exit()
            case _:
                print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()