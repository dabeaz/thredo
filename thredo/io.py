# io.py

__all__ = ['Socket']

# -- Standard Library

from socket import SOL_SOCKET, SO_ERROR
from contextlib import contextmanager
import io
import os

# -- Curio

from curio.traps import _read_wait, _write_wait
from curio.thread import TAWAIT as AWAIT
from curio.io import _Fd, WantRead, WantWrite
import curio.errors

# This socket class mirrors the functionality in the Curio socket
# class.  An important facet of the design is that it still relies
# upon non-blocking I/O and eager evaluation.  Curio only enters
# the picture if operations actually block.

class Socket(object):
    '''
    Non-blocking wrapper around a socket object.
    '''

    def __init__(self, sock):
        self._socket = sock
        self._socket.setblocking(False)
        self._fileno = _Fd(sock.fileno())

        # Commonly used bound methods
        self._socket_send = sock.send
        self._socket_recv = sock.recv

    def __repr__(self):
        return '<thredo.Socket %r>' % (self._socket)

    def __getattr__(self, name):
        return getattr(self._socket, name)

    def fileno(self):
        return int(self._fileno)

    def settimeout(self, seconds):
        if seconds:
            raise RuntimeError('Use timeout_after() to set a timeout')

    def gettimeout(self):
        return None

    def dup(self):
        return type(self)(self._socket.dup())

    def makefile(self, mode, buffering=0, *, encoding=None, errors=None, newline=None):
        if 'b' not in mode:
            raise RuntimeError('File can only be created in binary mode')
        f = self._socket.makefile(mode, buffering=buffering)
        return FileStream(f)

    def as_stream(self):
        return SocketStream(self._socket)

    def recv(self, maxsize, flags=0):
        while True:
            try:
                return self._socket_recv(maxsize, flags)
            except WantRead:
                AWAIT(_read_wait, self._fileno)
            except WantWrite:
                AWAIT(_write_wait, self._fileno)

    def recv_into(self, buffer, nbytes=0, flags=0):
        while True:
            try:
                return self._socket.recv_into(buffer, nbytes, flags)
            except WantRead:
                AWAIT(_read_wait, self._fileno)
            except WantWrite:
                AWAIT(_write_wait, self._fileno)

    def send(self, data, flags=0):
        while True:
            try:
                return self._socket_send(data, flags)
            except WantWrite:
                AWAIT(_write_wait, self._fileno)
            except WantRead: 
                AWAIT(_read_wait, self._fileno)

    def sendall(self, data, flags=0):
        with memoryview(data).cast('B') as buffer:
            total_sent = 0
            try:
                while buffer:
                    try:
                        nsent = self._socket_send(buffer, flags)
                        total_sent += nsent
                        buffer = buffer[nsent:]
                    except WantWrite:
                        AWAIT(_write_wait, self._fileno)
                    except WantRead: 
                        AWAIT(_read_wait, self._fileno)
            except curio.errors.CancelledError as e:
                e.bytes_sent = total_sent
                raise

    def accept(self):
        while True:
            try:
                client, addr = self._socket.accept()
                client = Socket(client)
                client.__class__ = type(self)
                return client, addr
            except WantRead:
                AWAIT(_read_wait, self._fileno)

    def connect_ex(self, address):
        try:
            self.connect(address)
            return 0
        except OSError as e:
            return e.errno

    def connect(self, address):
        try:
            result = self._socket.connect(address)
            if getattr(self, 'do_handshake_on_connect', False):
                self.do_handshake()
            return result
        except WantWrite:
            AWAIT(_write_wait, self._fileno)
        err = self._socket.getsockopt(SOL_SOCKET, SO_ERROR)
        if err != 0:
            raise OSError(err, 'Connect call failed %s' % (address,))
        if getattr(self, 'do_handshake_on_connect', False):
            self.do_handshake()

    def recvfrom(self, buffersize, flags=0):
        while True:
            try:
                return self._socket.recvfrom(buffersize, flags)
            except WantRead:
                AWAIT(_read_wait, self._fileno)
            except WantWrite:
                AWAIT(_write_wait, self._fileno)

    def recvfrom_into(self, buffer, bytes=0, flags=0):
        while True:
            try:
                return self._socket.recvfrom_into(buffer, bytes, flags)
            except WantRead:
                AWAIT(_read_wait, self._fileno)
            except WantWrite:
                AWAIT(_write_wait, self._fileno)

    def sendto(self, bytes, flags_or_address, address=None):
        if address:
            flags = flags_or_address
        else:
            address = flags_or_address
            flags = 0
        while True:
            try:
                return self._socket.sendto(bytes, flags, address)
            except WantWrite:
                AWAIT(_write_wait, self._fileno)
            except WantRead:
                AWAIT(_read_wait, self._fileno)

    def recvmsg(self, bufsize, ancbufsize=0, flags=0):
        while True:
            try:
                return self._socket.recvmsg(bufsize, ancbufsize, flags)
            except WantRead:
                AWAIT(_read_wait, self._fileno)

    def recvmsg_into(self, buffers, ancbufsize=0, flags=0):
        while True:
            try:
                return self._socket.recvmsg_into(buffers, ancbufsize, flags)
            except WantRead:
                AWAIT(_read_wait, self._fileno)

    def sendmsg(self, buffers, ancdata=(), flags=0, address=None):
        while True:
            try:
                return self._socket.sendmsg(buffers, ancdata, flags, address)
            except WantRead:
                AWAIT(_write_wait, self._fileno)

    # Special functions for SSL
    def do_handshake(self):
        while True:
            try:
                return self._socket.do_handshake()
            except WantRead:
                AWAIT(_read_wait, self._fileno)
            except WantWrite:
                AWAIT(_write_wait, self._fileno)

    def close(self):
        if self._socket:
            self._socket.close()
        self._socket = None
        self._fileno = -1

    def shutdown(self, how):
        if self._socket:
            self._socket.shutdown(how)



MAX_READ = 65536

class StreamBase(object):
    '''
    Base class for file-like objects.
    '''

    def __init__(self, fileobj):
        self._file = fileobj
        self._fileno = _Fd(fileobj.fileno())
        self._buffer = bytearray()

    def __repr__(self):
        return '<thredo.%s %r>' % (type(self).__name__, self._file)

    def fileno(self):
        return int(self._fileno)

    # ---- Methods that must be implemented in child classes
    def _read(self, maxbytes=-1):   
        raise NotImplementedError()

    def write(self, data):          
        raise NotImplementedError()

    # ---- General I/O methods for streams
    def read(self, maxbytes=-1):
        buf = self._buffer
        if buf:
            if maxbytes < 0 or len(buf) <= maxbytes:
                data = bytes(buf)
                buf.clear()
            else:
                data = bytes(buf[:maxbytes])
                del buf[:maxbytes]
        else:
            data = self._read(maxbytes)
        return data

    def readall(self):
        chunks = []
        maxread = 65536
        if self._buffer:
            chunks.append(bytes(self._buffer))
            self._buffer.clear()
        while True:
            try:
                chunk = self.read(maxread)
            except curio.errors.CancelledError as e:
                e.bytes_read = b''.join(chunks)
                raise
            if not chunk:
                return b''.join(chunks)
            chunks.append(chunk)
            if len(chunk) == maxread:
                maxread *= 2

    def read_exactly(self, nbytes):
        chunks = []
        while nbytes > 0:
            try:
                chunk = self.read(nbytes)
            except curio.errors.CancelledError as e:
                e.bytes_read = b''.join(chunks)
                raise
            if not chunk:
                e = EOFError('Unexpected end of data')
                e.bytes_read = b''.join(chunks)
                raise e
            chunks.append(chunk)
            nbytes -= len(chunk)
        return b''.join(chunks)

    def readinto(self, memory):
        with memoryview(memory).cast('B') as view:
            remaining = len(view)
            total_read = 0

            # It's possible that there is data already buffered on this stream. 
            # If so, we have to copy into the memory buffer first.
            buffered = len(self._buffer)
            tocopy = remaining if (remaining < buffered) else buffered
            if tocopy:
                view[:tocopy] = self._buffer[:tocopy]
                del self._buffer[:tocopy]
                remaining -= tocopy
                total_read += tocopy

            # To emulate behavior of synchronous readinto(), we read all available
            # bytes up to the buffer size.
            while remaining > 0:
                try:
                    nrecv = self._readinto_impl(view[total_read:total_read+remaining])

                    # On proper file objects, None might be returned to indicate blocking
                    if nrecv is None:
                        AWAIT(_read_wait, self._fileno)
                    elif nrecv == 0:
                        break
                    else:
                        total_read += nrecv
                        remaining -= nrecv
                except WantRead:
                    AWAIT(_read_wait, self._fileno)
                except WantWrite:
                    AWAIT(_write_wait, self._fileno)
            return total_read
        
    def readline(self, maxlen=None):
        while True:
            nl_index = self._buffer.find(b'\n')
            if nl_index >= 0:
                resp = bytes(self._buffer[:nl_index + 1])
                del self._buffer[:nl_index + 1]
                return resp
            data = self._read(MAX_READ)
            if data == b'':
                resp = bytes(self._buffer)
                self._buffer.clear()
                return resp
            self._buffer.extend(data)

    def readlines(self):
        lines = []
        try:
            for line in self:
                lines.append(line)
            return lines
        except curio.errors.CancelledError as e:
            e.lines_read = lines
            raise

    def writelines(self, lines):
        nwritten = 0
        for line in lines:
            try:
                self.write(line)
                nwritten += len(line)
            except curio.errors.CancelledError as e:
                e.bytes_written += nwritten
                raise

    def flush(self):
        pass

    def close(self):
        self.flush()
        if self._file:
            self._file.close()
        self._file = None
        self._fileno = -1

    def __iter__(self):
        return self

    def __next__(self):
        line = self.readline()
        if line:
            return line
        else:
            raise StopIteration

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.close()


class FileStream(StreamBase):
    '''
    Wrapper around a file-like object.  File is put into non-blocking mode.
    The underlying file must be in binary mode.
    '''

    def __init__(self, fileobj):
        assert not isinstance(fileobj, io.TextIOBase), 'Only binary mode files allowed'
        super().__init__(fileobj)
        os.set_blocking(int(self._fileno), False)

        # Common bound methods
        self._file_read = fileobj.read
        self._readinto_impl = getattr(fileobj, 'readinto', None)
        self._file_write = fileobj.write

    def _read(self, maxbytes=-1):
        while True:
            # In non-blocking mode, a file-like object might return None if no data is
            # available.  Alternatively, we'll catch the usual blocking exceptions just to be safe
            try:
                data = self._file_read(maxbytes)
                if data is None:
                    AWAIT(_read_wait, self._fileno)
                else:
                    return data
            except WantRead:
                AWAIT(_read_wait, self._fileno)
            except WantWrite: 
                AWAIT(_write_wait, self._fileno)

    def write(self, data):
        nwritten = 0
        view = memoryview(data).cast('B')
        try:
            while view:
                try:
                    nbytes = self._file_write(view)
                    if nbytes is None:
                        raise BlockingIOError()
                    nwritten += nbytes
                    view = view[nbytes:]
                except WantWrite as e:
                    if hasattr(e, 'characters_written'):
                        nwritten += e.characters_written
                        view = view[e.characters_written:]
                    AWAIT(_write_wait, self._fileno)
                except WantRead:
                    AWAIT(_read_wait, self._fileno)
            return nwritten

        except curio.errors.CancelledError as e:
            e.bytes_written = nwritten
            raise

    def flush(self):
        if not self._file:
            return
        while True:
            try:
                return self._file.flush()
            except WantWrite:
                AWAIT(_write_wait, self._fileno)
            except WantRead:
                AWAIT(_read_wait, self._fileno)

class SocketStream(StreamBase):
    '''
    Stream wrapper for a socket.
    '''

    def __init__(self, sock):
        super().__init__(sock)
        sock.setblocking(False)

        # Common bound methods
        self._socket_recv = sock.recv
        self._readinto_impl = sock.recv_into
        self._socket_send = sock.send

    def _read(self, maxbytes=-1):
        while True:
            try:
                data = self._socket_recv(maxbytes if maxbytes > 0 else MAX_READ)
                return data
            except WantRead:
                AWAIT(_read_wait, self._fileno)
            except WantWrite:
                AWAIT(_write_wait, self._fileno)

    def write(self, data):
        nwritten = 0
        view = memoryview(data).cast('B')
        try:
            while view:
                try:
                    nbytes = self._socket_send(view)
                    nwritten += nbytes
                    view = view[nbytes:]
                except WantWrite:
                    AWAIT(_write_wait, self._fileno)
                except WantRead:
                    AWAIT(_read_wait, self._fileno)
            return nwritten
        except curio.errors.CancelledError as e:
            e.bytes_written = nwritten
            raise
