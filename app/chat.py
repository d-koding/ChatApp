import socket # for socket programming
import threading # for each connection thread

from client import client
from server import server


def handle_help():
    """
    Display available commands and their usage
    """
    print("Available commands:")
    print("  myip                : Display the IP address of this device")
    print("  myport              : Display the port number this process runs on")
    print("  connect <ip> <port> : Establish a new TCP connection to the given destination")
    print("  list                : Display all active connections")
    print("  terminate <id>      : Terminate connection according to the list index")
    print("  send <id> <message> : Send a message to the host on the specified connection")
    print("  exit                : Close all connections and terminate this process")


def main():
    server()

    connections = []

    while True:
        message = input(">")
        message = message.strip()
        message_parts = message.split(" ")
        command = parts[0].lower()

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