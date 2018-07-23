# queue.py
#
# A basic queue

__all__ = [ 'Queue' ]

import curio
from curio.thread import TAWAIT as AWAIT

class Queue(object):
    def __init__(self, maxsize=0):
        self._queue = curio.Queue(maxsize)

    def empty(self):
        return self._queue.empty()

    def full(self):
        return self._queue.full()

    def get(self):
        return AWAIT(self._queue.get)

    def join(self):
        return AWAIT(self._queue.join)

    def put(self, item):
        return AWAIT(self._queue.put, item)

    def qsize(self):
        return self._queue.qsize()

    def task_done(self):
        return AWAIT(self._queue.task_done)

    def __iter__(self):
        return self

    def __next__(self):
        return self.get()
