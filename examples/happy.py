# happy.py
# An implementation of RFC 6555 (Happy Eyeballs)

from threadio import socket, ThreadGroup, spawn, ignore_after, run
import itertools

def open_tcp_stream(hostname, port, happy_eyeballs_delay=0.3):
    # Get all of the possible targets for a given host/port
    targets = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    if not targets:
        raise OSError(f'nothing known about {hostname}:{port}')

    # Group the targets into different address families
    families = { af: list(group)
                 for af, group in itertools.groupby(targets, key=lambda t: t[0]) }

    # Arrange the targets to interleave address families.
    targets = itertools.chain(*zip(*families.values()))

    # List of socket-related errors (if any)
    errors = []

    def try_connect(sock, addr):
        try:
            sock.connect(addr)
            print("Got:", sock)
            return sock
        except OSError as e:
            errors.append(e)
            sock.close()
            return None

    def connector(group):
        for *sockargs, _, addr in targets:
            sock = socket.socket(*sockargs)
            task = group.spawn(try_connect, sock, addr)
            with ignore_after(happy_eyeballs_delay):
                task.wait()
        print("here!")

    with ThreadGroup(wait=any) as g:
         g.spawn(connector, g)

    if g.completed:
        return g.completed.result
    else:
        raise OSError(errors)

def main():
    result = open_tcp_stream('www.python.org', 80)
    print(result)

if __name__ == '__main__':
    run(main)


    
    
    

    
    
    
