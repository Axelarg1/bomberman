import threading
import socket
import time
import re


class Client():

    def __init__(self, username, server, port, callback):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))
        self.username = username
        self.send("USERNAME {0}".format(username))
        self.listening = True
        self.callback = callback

    def listener(self):
        while self.listening:
            data = ""
            try:
                data = self.socket.recv(1024).decode('UTF-8')
            except socket.error:
                print("Unable to receive data")
            self.handle_msg(data)
            time.sleep(0.1)

    def listen(self):
        self.listen_thread = threading.Thread(target=self.listener)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def send(self, message):
        print("test2",message)
        try:
            username_result = re.search('^USERNAME (.*)$', message)
            self.socket.sendall(message.encode("UTF-8"))
        except socket.error:
            print("unable to send message")

    # de moi
    def received(self):
        try:
            self.socket.recv(2048)
        except socket.error:
            print("unable to received")

    def tidy_up(self):
        self.listening = False
        self.socket.close()

    def handle_msg(self, data):
        if data == "QUIT":
            self.tidy_up()
        elif data == "":
            self.tidy_up()
        else:
            print("Received JSON:", data)
            self.callback(data)


if __name__ == "__main__":
    username = input("username: ")
    server = input("server: ")
    port = int(input("port: "))
    client = Client(username, server, port)  # type: ignore
    client.listen()
    message = ""
    while message != "QUIT":
        message = input()
        client.send(message)
