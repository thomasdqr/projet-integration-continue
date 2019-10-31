import socket
import sys
import traceback
from threading import Thread
import json
import conf
from datetime import datetime

class Game:
    def __init__(self, players):
        print("game créée")
        self.test = 0
        self.questions = ["Combien de coupe du monde on gagne le Bresil ?", "Combien de ballon d'or a gagné cristiano ronaldo"]
        self.answer = ["5", "6"]
        self.players = players
        self.cptQuestion = 0
        self.response = {}
        self.tab_score = {}
        self.create_tab_score()
        self.send_question()
        
    def send_message(self, action, message):
        print("send_message", action)
        for player in self.players:
            # print(player.name)
            player.connection.send(json.dumps({"action" : action, "message" : message}).encode("utf-8"))
    
    def create_tab_score(self):
        for player in self.players:
            self.tab_score[player.name] = 0
    
    def send_question(self):
        print("send question function")
        for player in self.players:
            player.connection.send(json.dumps({'action' : 'sendQuestion', 'question' : self.questions[self.cptQuestion]}).encode('utf-8'))
        # print("test")
        if self.test == 0:
            self.test += 1
            # self.check_time_response()

    def add_response(self, player, response):
        self.response[player] = response
        # print(self.response)
        if len(self.response) == len(self.players):
            self.send_message("close_thread", "")
            self.score()
            self.response = {}

    def score(self):
        print('--- Score ---')
        no_good_answer = 1
        for rep in self.response:
            # print("0")
            if self.response[rep] == self.answer[self.cptQuestion]:
                no_good_answer = 0
                # print("1")
                self.tab_score[rep] += 1
                self.send_message("score", self.tab_score)
                self.cptQuestion += 1
                if len(self.questions) > self.cptQuestion:
                    # print("2")
                    self.send_question()
                else:
                    # print("3")
                    self.send_message("exit", "La partie est terminer")
                break
        if no_good_answer == 1:
            self.send_message("score", self.tab_score)
            self.cptQuestion += 1
            if len(self.questions) > self.cptQuestion:
                # print("5")
                self.send_question()
            else:
                # print("6")
                self.send_message("exit", "La partie est terminer")

    # def check_time_response(self):
    #     timestamp1 = datetime.timestamp(datetime.now())
    #     print("check_time_response")
    #     while True:
    #         timestamp2 = datetime.timestamp(datetime.now())
    #         dif = timestamp2 - timestamp1
    #         print(dif)
    #         if dif > 5.0:
    #             print("Limite temps")
    #             self.score()
    #             break
    
class Player:
    def __init__(self, ip, connection):
        self.ip = ip
        self.connection = connection
        
    def inscription(self, name):
        self.name = name
        self.print_name()

    def print_name(self):
        print(self.name)

class Server:
    def __init__(self, conf):
        self.host = conf.get("host")
        self.port = conf.get("port")
        self.players = []

    def start_server(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
        print("Socket created")

        try:
            soc.bind((self.host, self.port))
        except:
            print("Bind failed. Error : " + str(sys.exc_info()))
            sys.exit()

        soc.listen(5)
        print("Socket now listening")
        while True:
            connection, address = soc.accept()
            ip, port = str(address[0]), str(address[1])
            print("Connected with " + ip + ":" + port)
            MyClient = Player(ip, connection)
            try:
                Thread(target=self.client_thread, args=(connection, ip, port, MyClient)).start()
            except:
                print("Thread did not start.")
                traceback.print_exc()

        soc.close()
    
    def client_thread(self, connection, ip, port, MyClient,  max_buffer_size = 1024):
        try:
            is_active = True
            while is_active:
                client_input = connection.recv(max_buffer_size)
                request = json.loads(client_input.decode('utf-8'))
                if request["action"] == "inscription":
                    MyClient.inscription(request["name"])
                    self.players.append(MyClient)
                    self.luncher_game()
                if request["action"] == "print_name":
                    MyClient.print_name()
                if request["action"] == "response":
                    self.game.add_response(request["player"], request["response"])
        except:
            self.players.remove(MyClient)
            self.game.players = self.players
            print(MyClient.name, "c'est déconecter")  


    def luncher_game(self):
        if len(self.players) >= 2:
            self.game = Game(self.players)


def main(conf):
    server = Server(conf)
    server.start_server()


if __name__ == "__main__":
    main(conf.MyConf)