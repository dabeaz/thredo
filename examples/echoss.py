# Echo server implemented using socket server and 
# a ThredoMixIn class.   This class replaces the normal
# socket with one that can be cancelled.  Also uses spawn()
# internally to launch threads.

from thredo.socket import *
import thredo
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
        except thredo.ThreadCancelled:
            print('Handler Cancelled')
        print('Connection closed')

class EchoStreamHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print("Stream Connection from", self.client_address)
        try:
            for line in self.rfile:
                self.wfile.write(line)
        except thredo.ThreadCancelled:
            print('Stream Handler Cancelled')
        print('Stream Connection closed')

class ThredoTCPServer(thredo.ThredoMixIn, socketserver.TCPServer):
    pass
    allow_reuse_address = True

def main():
#    serv = ThredoTCPServer(('', 25000), EchoHandler)
    serv = ThredoTCPServer(('', 25000), EchoStreamHandler)
    serv.allow_reuse_address = True
    t = thredo.spawn(serv.serve_forever)
    thredo.SignalEvent(signal.SIGINT).wait()
    print('Cancelling')
    t.cancel()

thredo.run(main)

    
