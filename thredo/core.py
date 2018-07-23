# core.py

__all__ = ['run', 'sleep', 'spawn', 'timeout_after', 'ignore_after',
           'ThreadTimeout', 'ThreadCancelled', 'CancelledError',
           'ThreadError', 'ThreadGroup']

import curio
AWAIT = curio.thread.TAWAIT

class Thread:
    def __init__(self, atask):
        self.atask = atask

    def cancel(self):
        AWAIT(self.atask.cancel)

    def join(self):
        return AWAIT(self.atask.join)

    def wait(self):
        return AWAIT(self.atask.wait)

class ThreadGroup:
    def __init__(self, *args, **kwargs):
        self._tg = curio.TaskGroup(*args, **kwargs)

    def spawn(self, callable, *args, daemon=False):
        t = AWAIT(curio.spawn_thread, callable, *args, daemon=daemon)
        AWAIT(self._tg.add_task, t)
        return Thread(t)

    def cancel(self, *args, **kwargs):
        AWAIT(self._tg.cancel, *args, **kwargs)

    def cancel_remaining(self, *args, **kwargs):
        AWAIT(self._tg.cancel_remaining, *args, **kwargs)

    def join(self, *args, **kwargs):
        return AWAIT(self._tg.cancel, *args, **kwargs)

    def next_result(self, *args, **kwargs):
        return AWAIT(self._tg.next_result, *args, **kwargs)

    def next_done(self, *args, **kwargs):
        return AWAIT(self._tg.next_done, *args, **kwargs)

    def __enter__(self):
        self._tg.__enter__()
        return self

    def __exit__(self, *args):
        return self._tg.__exit__(*args)

    @property
    def completed(self):
        return self._tg.completed


def run(callable, *args):
    async def _runner():
        t = await curio.spawn(curio.thread.thread_handler)
        try:
            async with curio.spawn_thread():
                return callable(*args)
        finally:
            await t.cancel()
    return curio.run(_runner)

def enable():
    curio.thread.enable_async()

def sleep(seconds):
    return AWAIT(curio.sleep, seconds)

def spawn(callable, *args, daemon=False):
    atask = AWAIT(curio.spawn_thread, callable, *args, daemon=daemon)
    return Thread(atask)

def timeout_after(delay, callable=None, *args):
    curio.thread.enable_async()
    if callable:
        with curio.timeout_after(delay):
            return callable(*args)
    else:
        return curio.timeout_after(delay)

def ignore_after(delay, callable=None, *args):
    curio.thread.enable_async()
    if callable:
        with curio.ignore_after(delay):
            return callable(*args)
    else:
        return curio.ignore_after(delay)

ThreadTimeout = curio.TaskTimeout
ThreadCancelled = curio.TaskCancelled
CancelledError = curio.CancelledError
ThreadError = curio.TaskError



