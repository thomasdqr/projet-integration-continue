import socket
import sys
import json
import conf
import threading
from datetime import datetime

class Client:
    def __init__(self, conf):
        self.host = conf.get("host")
        self.port = conf.get("port")
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rep = 0
        self.tabThreads = []

    def start_client(self):
        try:
            self.soc.connect((self.host, self.port))
            self.connection()
        except:
            print("Connection error")
            sys.exit()
    
    def connection(self):
        print("Qu'elle est votre nom ?")
        self.name = input(" -> ")
        self.soc.send(json.dumps({'action' : 'inscription', 'name' : self.name}).encode('utf-8'))
        self.listening()

    def listening(self):
        print("listening")
        try:
            is_active = True
            while is_active:
                server_input = self.soc.recv(1024)
                request = json.loads(server_input.decode('utf-8'))
                if request["action"] == "sendQuestion":
                    # question = str(request["question"])
                    # print("receiv question")
                    # t1 = threading.Thread(target=self.question, args=(question,))
                    t2 = threading.Thread(target=self.check_time_response)
                    # print("socket in tab")
                    # self.tabThreads.append(t1)
                    self.tabThreads.append(t2)
                    # t1.start()
                    t2.start()
                    # print("socket created")
                    # self.question(request["question"])
                if request["action"] == "score":
                    self.print_score(request["message"])
                if request["action"] == "exit":
                    self.exit(request["message"])
                if request["action"] == "close_thread":
                    self.close_thread()
        except:
            # print("Vous êtes déconecter")
            print("Bind failed. Error : " + str(sys.exc_info()))
    
    def question(self, question):
        print(question)
        response = input('->')
        self.rep = 1
        self.soc.send(json.dumps({"action" : "response", "player" : self.name, "response": response}).encode('utf-8'))
        # self.close_thread()
    
    def message(self, message):
        print(message)
    
    def print_score(self, scores):
        print('--- print_score ---')
        for score in scores:
            print(score, ":", scores[score])
    
    def exit(self, message):
        print(message)
        sys.exit()
    
    def check_time_response(self):
        print(' --- check_time_response function ---')
        timestamp1 = datetime.timestamp(datetime.now())
        while True:
            timestamp2 = datetime.timestamp(datetime.now())
            dif = timestamp2 - timestamp1
            # print(dif)
            if dif > 10.0 and self.rep == 0:
                print("--- Limite temps ---")
                dif = 0
                self.soc.send(json.dumps({"action" : "response", "player" : self.name, "response": ""}).encode('utf-8'))
                # self.close_thread()
                break
    
    def close_thread(self):
        print("--- close function ---")
        for thread in self.tabThreads:
            print (thread)


def main(conf):
    client = Client(conf)
    client.start_client()

if __name__ == "__main__":
    main(conf.MyConf)