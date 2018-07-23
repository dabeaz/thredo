# requests.py
#
# Session adapter that allows requests to use thredo socket objects.
# This is a bit of plumbing, but it's a clean interface that doesn't
# require any monkeypatching or other low-level magic

__all__ = ['get_session']

# -- Thredo
from . import socket

# -- Requests/third party
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import PoolManager, HTTPConnectionPool
from requests.packages.urllib3 import HTTPSConnectionPool
from http.client import HTTPConnection, HTTPSConnection

class ThredoAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block):
        self.poolmanager = ThredoPoolManager(num_pools=connections,
                                               maxsize=maxsize,
                                               block=block)


class ThredoPoolManager(PoolManager):
    def _new_pool(self, scheme, host, port):
        # Important!
        if scheme == 'http':
            return ThredoHTTPConnectionPool(host, port, **self.connection_pool_kw)

        if scheme == 'https':
            return ThredoHTTPSConnectionPool(host, port, **self.connection_pool_kw)

        return super(PoolManager, self)._new_pool(self, scheme, host, port)


class ThredoHTTPConnectionPool(HTTPConnectionPool):
    def _new_conn(self):
        self.num_connections += 1
        return ThredoHTTPConnection(host=self.host,
                            port=self.port)


class ThredoHTTPSConnectionPool(HTTPSConnectionPool):
    def _new_conn(self):
        self.num_connections += 1
        return ThredoHTTPSConnection(host=self.host,
                            port=self.port)


class ThredoHTTPConnection(HTTPConnection):
    def connect(self):
        """Connect to the host and port specified in __init__."""
        # Uses thredo
        self.sock = socket.create_connection((self.host, self.port),
                                             self.timeout, self.source_address)
        # Important!
        if self._tunnel_host:
            self._tunnel()

class ThredoHTTPSConnection(HTTPSConnection):
    def connect(self):
        """Connect to the host and port specified in __init__."""
        # Uses thredo
        self.sock = socket.create_connection((self.host, self.port),
                                             self.timeout, self.source_address)
        # Important!
        if self._tunnel_host:
            server_hostname = self._tunnel_host
        else:
            server_hostname = self.host
            
        self.sock = self._context.wrap_socket(self.sock, server_hostname=server_hostname)

def get_session():
    s = requests.Session()
    s.mount('http://', ThredoAdapter())
    s.mount('https://', ThredoAdapter())
    return s

