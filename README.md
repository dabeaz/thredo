# thredo

Thredo is threads on async.  For the brave. Or the foolish. Only time will tell.

## High Level Overview (The Big Idea)

Consider the following thread program involving a worker, a producer,
and queue::

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

In this code, there are blocking operations such as ``q.get()`` and
``time.sleep()``.  This blocking is ultimately handled by the
host operating system.  Because of that, it is very difficult for
Python to do anything related to the actual control or scheduling
of threads.  Once blocked, a thread stays blocked forever or until
some event occurs that causes it to unblock.

Thredo re-envisions threads by redirecting all blocking operations to
an async library.  The code looks mostly the same except that you use 
the `thredo` module. For example:

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

The main reason you'd use ``thredo`` however is that it gives you extra
features such as thread groups, cancellation, and more.   For example,
here's a more advanced version of the above code::

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

== Examples

The ``examples`` directory contains more examples of using ``thredo``. 
The ``examples/euro`` directory contains coding samples from the
EuroPython 2018 talk.




