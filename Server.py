import socket
import signal  # identifie les signaux pour kill le programme
import sys  # utilisÃ© pour sortir du programme
import time
import json
from clientthread import ClientListener

# players_number = 0

class Server():
    global ready
    ready = []

    def __init__(self, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(('', port))
        self.listener.listen(1)
        print("Listening on port", port)
        self.clients_sockets = []
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signal, frame):
        self.listener.close()
        self.echo("QUIT")

    def run(self):

        while True:
            print("listening new customers")
            try:
                # players_number = 1
                (client_socket, client_adress) = self.listener.accept()
            except socket.error:
                sys.exit("Cannot connect clients")
            self.clients_sockets.append(client_socket)
            print("Start the thread for client:", client_adress)
            client_thread = ClientListener(self, client_socket, client_adress)
            client_thread.start()
            time.sleep(0.1)

    def remove_socket(self, socket):
        self.clients_sockets.remove(socket)
        # players_number -= 1
        print("ready",ready)

    def echo(self, data):
        test = ""
        print("me",data,type(data),data[0])
        if (data[0] != "{"):
            if(data[0] == "p"):
                test = str(len(self.clients_sockets))+"_"
            else:
                ready.append('1')

        data = test+data
        test = ""
        # if(len(ready) = len(self.clients_sockets)):
        #     for sock in self.clients_sockets:
        #         try:
        #             sock.sendall(data.encode("UTF-8"))
        #         except socket.error:
        #             print("Cannot send ready")
        print("echoing:", test+data)
        for sock in self.clients_sockets:
            try:
                sock.sendall(data.encode("UTF-8"))
            except socket.error:
                print("Cannot send the message")

if __name__ == "__main__":
    server = Server(59001)
    server.run()
