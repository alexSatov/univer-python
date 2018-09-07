# Сети
# socket
# 65336 портов в ОС
# передаются пакеты через порт (от 1 ip ко 2)
#
# socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
# HOST = ''
# PORT = 50007
# #                          ip_v4            TCP
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen(1)
#     conn, addr = s.accept()
#     with conn:
#         print('Connected by ', addr)
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             conn.sendall(data)
#
# HOST = 'dating.cwi.nl'
# PORT = 50007
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b'Hello world')
#     data = s.recv(1024)
# print('Recieved', data)

import socket
import threading

HOST = 'localhost'
PORT = 50007


class Chat:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

    def start(self):
        self.s.bind((HOST, PORT))
        self.s.listen(1)
        while 1:
            conn, addr = self.s.accept()
            self.clients.append(conn)
            thread = threading.Thread(
                target=self.client_work,
                args=(conn, addr)
            )
            thread.start()
        self.s.close()

    def client_work(self, conn, addr):
        print('Connected by ', addr)
        while True:
            data = conn.recv(1024)
            print('recv: ', repr(data))
            if not data:
                break
            for client in self.clients:
                client.sendall(data)
            conn.close()
            self.clients.remove(conn)

c = Chat()
c.start()

