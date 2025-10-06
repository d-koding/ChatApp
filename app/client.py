import socket # for socket programming


def client(ip_address, port_number):
    # create a socket
    s = socket.socket()

    # connect to the server using the known listening port
    s.connect((ip_address, port_number))

    # keep getting user input
    while True:
        message = input(">")
        
        # encode the message to bytes and send using the socket
        s.send(message.encode())
        
        # print replies from server
        data = s.recv(1024)
        print(data.decode())
        if message == "close":
            break

    s.close()

if __name__ == "__main__":
    client()
