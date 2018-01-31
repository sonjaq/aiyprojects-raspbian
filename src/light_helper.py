import socket


def send_light_command(command):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 7777))
    clientsocket.send(command.encode())


