# Simple echo server benchmark

from threadio.socket import *
import threadio

def echo_handler(client, addr):
    print('Connection from', addr)
    try:
        f = client.makefile('rb')
        g = client.makefile('wb')
        for line in f:
            g.write(line)
    finally:
        print('Connection closed')
        f.close()
        g.close()
        client.close()

def killer(delay, t):
    threadio.sleep(delay)
    t.cancel()

def echo_server(host, port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((host,port))
    sock.listen(5)
    while True:
        client, addr = sock.accept()
        t = threadio.spawn(echo_handler, client, addr, daemon=True)
        threadio.spawn(killer, 30, t)
        
threadio.run(echo_server, '', 25000)

    
