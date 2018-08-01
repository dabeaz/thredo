# thredo

Thredo is threads on async.  For the brave. Or the foolish. Only time will tell.

Note: Thredo requires the most up-to-date version of Curio--meaning the one
that is checked out of the Curio GitHub repository at https://github.com/dabeaz/curio.

## High Level Overview (The Big Idea)

Consider the following thread program involving a worker, a producer,
and queue:
```python
import threading
import queue
import time

def worker(q):
    while True:
        item = q.get()
        if item is None:
            break
        print('Got:', item)

def main():
    q = queue.Queue()
    t = threading.Thread(target=worker, args=(q,))
    t.start()
    for n in range(10):
        q.put(n)
        time.sleep(1)
    q.put(None)
    t.join()

main()
```

In this code, there are blocking operations such as ``q.get()`` and
``time.sleep()``.  This blocking is ultimately handled by the
host operating system.  Because of that, it is very difficult for
Python to do anything related to the actual control or scheduling
of threads.  Once blocked, a thread stays blocked forever or until
some event occurs that causes it to unblock.

Thredo re-envisions threads by redirecting all blocking operations to
an async library.  The code looks mostly the same except that you use 
the `thredo` module. For example:
```python
import thredo

def worker(q):
    while True:
        item = q.get()
        if item is None:
            break
        print('Got:', item)

def main():
    q = thredo.Queue()
    t = thredo.spawn(worker, q)
    for n in range(10):
        q.put(n)
        thredo.sleep(1)
    q.put(None)
    t.join()

thredo.run(main)
```

The main reason you'd use ``thredo`` however is that it gives you extra
features such as thread groups, cancellation, and more.   For example,
here's a more advanced version of the above code:
```python
import thredo

def worker(q):
    try:
        while True:
            item = q.get()
            print('Got:', item)
            q.task_done()
    except thredo.ThreadCancelled:
        print('Worker cancelled')

def main():
    q = thredo.Queue()
    with thredo.ThreadGroup(wait=None) as workers:
        for n in range(4):
            workers.spawn(worker, q)

        for n in range(10):
            q.put(n)
            thredo.sleep(1)

        workers.join()    

thredo.run(main)
```

## Examples

The ``examples`` directory contains more examples of using ``thredo``. 
The ``examples/euro`` directory contains coding samples from the
EuroPython 2018 talk.

## FAQ

**Q: Is this going to turn into a full-fledged project?**

A: It's too early to say.

**Q: Isn't this sort of like using concurrent.futures?**

A: No. concurrent.futures provides no mechanism for controlling threads and no mechanism for
cancelling threads.  Although it might appear like this is so, given that you can seemingly
"cancel" a Future, this has no effect on thread execution. Once started, worked submitted to a
thread pool in concurrent.futures runs to completion regardless of whether or not the associated Future
is cancelled. Cancelling a future really only causes it to be abandoned if it hasn't yet started.
If you cancel a thread in thredo, it is cleanly cancelled at the next blocking operation.



 

