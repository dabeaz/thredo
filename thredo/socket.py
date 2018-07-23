# socket.py
#
# Standin for the standard socket library.  The entire contents of stdlib socket are
# made available here.  

import socket as _socket

__all__ = _socket.__all__

from socket import *
from socket import _GLOBAL_DEFAULT_TIMEOUT

from functools import wraps
from . import io
import sys
    
@wraps(_socket.socket)
def socket(*args, **kwargs):
    return io.Socket(_socket.socket(*args, **kwargs))

class socket(io.Socket):
    def __init__(self, *args, **kwargs):
        super().__init__(_socket.socket(*args, **kwargs))

#    @staticmethod
#    def __new__(cls, *args, **kwargs):
#        return super().__new__(cls, _socket.socket(*args, **kwargs))

@wraps(_socket.socketpair)
def socketpair(*args, **kwargs):
    s1, s2 = _socket.socketpair(*args, **kwargs)
    return io.Socket(s1), io.Socket(s2)

@wraps(_socket.fromfd)
def fromfd(*args, **kwargs):
    return io.Socket(_socket.fromfd(*args, **kwargs))

# Replacements for blocking functions related to domain names and DNS

@wraps(_socket.create_connection)
def create_connection(*args, **kwargs):
    sock = _socket.create_connection(*args, **kwargs)
    return io.Socket(sock)


