import socket
import signal  # identifie les signaux pour kill le programme
import sys  # utilisÃ© pour sortir du programme
import time
import json
from clientthread import ClientListener

# players_number = 0

class Server():
    # global ready
    # ready = []

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
        # print("ready",ready)

    def echo(self, data):
        test = "" #Déclaration vide qui déterminera le préfixe attribué à chaque joueurs connectés
        # print("me",data,type(data),data[0])
        if (data[0] != "{"): #Vérifie si le text reçu n'est pas un objet stringifié
            if(data[0] == "p"): #Vérifie si le text est "player"
                test = str(len(self.clients_sockets))+"_"   #Si oui alors le préfixe devient le numéro correspondant à la place qu'il prend dans la list des clients connecté
            else:
                ready.append('1')
        elif(len(data)>42): #Sinon, puisqu'il s'agit bien d'un objet. Si la chaîne de caractère est plus longue que 42 (Vérification pour évité le bug des double objets un envoi causé par l'envoi massif de donnés))
            data = data[0:41] #On fait slice pour supprimer le doublon
            try: #Puis on essais de voir si un json fonction dessus (Car si ça ne fonctionne pas, ça signifie que le 1ère objets stringifié faisait 40 caratères et que donc le 41ème caratère est un "{" (le début du doublon) )
                testo = json.loads(data)
                # print("réussi",data,len(data))
            except: #Si ça n'a effectivement pas marché alors on retire le "{" en trop
                data = data[0:len(data)-1]
        data = test+data #On ajoute le préfixe à la donnée (EX: Devient 1_player si c'est le joueur 1)
        test = "" #On remet à vide le préfixe
        # if(len(ready) = len(self.clients_sockets)):
        #     for sock in self.clients_sockets:
        #         try:
        #             sock.sendall(data.encode("UTF-8"))
        #         except socket.error:
        #             print("Cannot send ready")
        print("echoing:", test+data)
        for sock in self.clients_sockets:   #Pour chaque client connectés
            try:
                sock.sendall(data.encode("UTF-8")) #On envoi la donnée qu'il recevra dans le callback
            except socket.error:
                print("Cannot send the message")

if __name__ == "__main__":
    server = Server(59001)
    server.run()
