# thr.py
#
# Functions that allow normal threads to promote into Curio async threads.

from concurrent.futures import Future
from curio.thread import is_async_thread, _locals, AWAIT, AsyncThread
from curio import spawn, UniversalQueue

_request_queue = None

def TAWAIT(coro, *args, **kwargs):
    '''
    Ensure that the caller is an async thread (promoting if necessary),
    then await for a coroutine
    '''
    if not is_async_thread():
        enable_async()
    return AWAIT(coro, *args, **kwargs)

def thread_atexit(callable):
    _locals.thread_exit.atexit(callable)

def enable_async():
    '''
    Enable asynchronous operations in an existing thread.  This only
    shuts down once the thread exits.
    '''
    if hasattr(_locals, 'thread'):
        return

    if _request_queue is None:
        raise RuntimeError('Curio: enable_threads not used')

    fut = Future()
    _request_queue.put(('start', threading.current_thread(), fut))
    _locals.thread = fut.result()
    _locals.thread_exit = ThreadAtExit()
    
    def shutdown(thread=_locals.thread, rq=_request_queue):
        fut = Future()
        rq.put(('stop', thread, fut))
        fut.result()
    _locals.thread_exit.atexit(shutdown)

async def thread_handler():
    '''
    Special handler function that allows Curio to respond to
    threads that want to access async functions.   This handler
    must be spawned manually in code that wants to allow normal
    threads to promote to Curio async threads.
    '''
    global _request_queue
    assert _request_queue is None, "thread_handler already running"
    _request_queue = queue.UniversalQueue()

    try:
        while True:
            request, thr, fut = await _request_queue.get()
            if request == 'start':
                athread = AsyncThread(None)
                athread._task = await spawn(athread._coro_runner, daemon=True)
                athread._thread = thr
                fut.set_result(athread)
            elif request == 'stop':
                thr._request.set_result(None)
                await thr._task.join()
                fut.set_result(None)
    finally:
        _request_queue = None
    
