import socket
import threading

def handle_connection(connection_socket, address):
    """
    Handle messages from a connected peer.
    """
    while True:
        data = connection_socket.recv(1024)
        if not data:
            break

        message = data.decode()
        print("Got message from", address, ":", message)

        # Echo back in uppercase
        connection_socket.send(message.upper().encode())

        if message.lower() == "close":
            break

    connection_socket.close()


def start_server(port):
    """
    Start a server socket listening on the given port.
    Returns the socket so the main shell can access it.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", port))
    s.listen(10)
    print(f"Server listening on port {port}")

    # Run the accept loop in a background thread
    def accept_loop():
        while True:
            conn, addr = s.accept()
            print("Got connection from", addr)
            threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()

    threading.Thread(target=accept_loop, daemon=True).start()

    return s
