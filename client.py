import socket
from time import sleep
import threading

HOST = 'localhost'
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


def reader():
    while 1:
        data = s.recv(1024)
        if not data:
            break
        print('recv: ', repr(data))
        s.close()

threading.Thread(target=reader, daemon=False).start()

for x in range(100):
    s.sendall(b'Hello, ' + str(x).encode())
    print('send: ', x)
    sleep(1)

s.close()
#print('Recieved', repr(data))
