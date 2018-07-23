# Echo server implemented using socket server and 
# a ThreadioMixIn class.   This class replaces the normal
# socket with one that can be cancelled.  Also uses spawn()
# internally to launch threads.

from threadio.socket import *
import threadio
import socketserver
import signal

class EchoHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("Connection from", self.client_address)
        try:
            while True:
                data = self.request.recv(100000)
                if not data:
                    break
                self.request.sendall(data)
        except threadio.ThreadCancelled:
            print('Handler Cancelled')
        print('Connection closed')

class EchoStreamHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print("Stream Connection from", self.client_address)
        try:
            for line in self.rfile:
                self.wfile.write(line)
        except threadio.ThreadCancelled:
            print('Stream Handler Cancelled')
        print('Stream Connection closed')

class ThreadioTCPServer(threadio.ThreadioMixIn, socketserver.TCPServer):
    pass
    allow_reuse_address = True

def main():
#    serv = ThreadioTCPServer(('', 25000), EchoHandler)
    serv = ThreadioTCPServer(('', 25000), EchoStreamHandler)
    serv.allow_reuse_address = True
    t = threadio.spawn(serv.serve_forever)
    threadio.SignalEvent(signal.SIGINT).wait()
    print('Cancelling')
    t.cancel()

threadio.run(main)

    
