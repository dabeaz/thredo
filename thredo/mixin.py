# mixin.py

__all__ = ['ThredoMixIn']

from . import io
from . import core

class ThredoMixIn:
    '''
    Mixin class that can be used to make standard socketserver objects to
    use thredo
    '''
    _threads = None

    def server_activate(self):
        super().server_activate()
        self.socket = io.Socket(self.socket)

    def serve_forever(self):
        while True:
            self.handle_request()
        
    def handle_request(self):
        try:
            self._handle_request_noblock()
        except core.ThreadCancelled:
            threads = self._threads
            self._threads = None
            if threads:
                for thread in threads:
                    thread.cancel()
            raise

    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        t = core.spawn(self.process_request_thread, request, client_address)
        if self._threads is None:
            self._threads = []
        self._threads.append(t)

    def server_close(self):
        super().server_close()
        threads = self._threads
        self._threads = None
        if threads:
            for thread in threads:
                thread.join()


