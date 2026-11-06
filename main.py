import os
import socket
import argparse
import sys
import threading
import csv

class Main():
    def __init__(self, ip='0.0.0.0', port=9001, csvFile='questions.csv'):
        self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.csvFile = csvFile

        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)



    def recvall(self, soc):
        while True:
            response = ''
            data_len = 1
            while data_len:
                data = soc.recv(1024)
                data_len = len(data)
                response += data.decode()
                if data_len < 1024:
                    break
            if response:
                return response
            else:
                return ''



    def client(self):
        self.soc.connect((self.ip, self.port))
        while True:
            response = self.recvall(self.soc)
            # response = ''
            # data_len = 1
            # while data_len:
            #     data = self.soc.recv(1024)
            #     print('receved')
            #     data_len = len(data)
            #     response += data.decode()
            #     if data_len < 1024:
            #         break
            # if response:
            print(response)
            if "EXIT" in response:
                print("\x1B]111")
                sys.exit(0)
            buffer = input("> ")
            self.soc.sendall(buffer.encode())



    def server(self):
        print("\x1B[1;1H\x1B[2J")
        ###
        self.questions = self.csv_reading()
        self.maxGrade = len(self.questions)
        for line in self.questions:
            print(f"=>{line[1]}")
            for ans in line[2:]:
                print(ans)
            print(f"answer is = {line[0]}\n")


        self.soc.bind((self.ip, self.port))
        print(f"[-] started listening on port {self.port}")
        self.soc.listen(5)
        while True:
            clientSocket, clientAddress = self.soc.accept()
            print(f"[*] got connection from {clientAddress[0]}:{clientAddress[1]}")
            clientThread = threading.Thread(target=self.client_handler, args=(clientSocket,))
            clientThread.start()



    def client_handler(self, clientSocket):
        message = ''
        message = "\x1B[1;1H\x1B[2J\x1B[1m\x1B[3m\x1B[31m\x1B[43m\x1B]11;#002b36\a===============[ welcome to the quiz ]===============\x1B[0m"
        ###
        message += "\n\nWrite your name"
        clientSocket.sendall(message.encode())
        response = clientSocket.recv(1024).decode()
        name = response
        wrongAns = 0
        for q in self.questions:
            print(q)
            message = f"\x1B[3;1H\x1B[2J==> {q[1]}\n"
            ###
            message += f"{q[2]}\n"
            message += f"{q[3]}\n"
            message += f"{q[4]}\n"
            message += f"{q[5]}\n"
            clientSocket.sendall(message.encode())
            response = self.recvall(clientSocket)
            if response == q[0]:
                print('correct')
                continue
            wrongAns += 1
            print('false')
        grade = str(round((self.maxGrade - wrongAns)/self.maxGrade*100)) + '%'
        result = f'"{name}","{grade}"'
        message = "you got ==> " + grade + "\nEXIT"
        clientSocket.sendall(message.encode())
        os.system(f'echo {result} >> res.csv')




    def csv_reading(self):
        with open(self.csvFile) as q:
            csv_reader = csv.reader(q)
            next(csv_reader)
            return list(csv_reader)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="client/server quiz application with RCE exploit"
            )
    parser.add_argument('-c', '--client', action="store_true", help="activate client mod")
    parser.add_argument('-s', '--server', action="store_true", help="activate server mod")
    args = parser.parse_args()
    obj = Main()
    if not (args.server ^ args.client):
        print("select server or client only")
        sys.exit(1)

    if args.client:
        obj.client()
    else:
        obj.server()

