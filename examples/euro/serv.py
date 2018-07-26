from socket import *
import random
import time

def server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    while True:
        client, addr = sock.accept()
        handler(client, addr)

def handler(client, address):
    time.sleep(random.randint(5,20))
    client.sendall(b'HTTP/1.0 200 OK\r\n\r\nDie Threads!\n')
    client.close()

if __name__ == '__main__':
    server(('',8000))
