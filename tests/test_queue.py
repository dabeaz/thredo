# test_queue.py

import thredo

def test_queue_simple():
    results = []
    def consumer(q):
        while True:
            item = q.get()
            if item is None:
                break
            results.append(item)
            q.task_done()
        q.task_done()
    
    def producer(q):
        results.append('start')
        for n in range(3):
            q.put(n)
        q.put(None)
        q.join()
        results.append('done')
        
    def main():
        q = thredo.Queue()
        t1 = thredo.spawn(consumer, q)
        t2 = thredo.spawn(producer, q)
        t1.join()
        t2.join()

    thredo.run(main)
    assert results == ['start', 0, 1, 2, 'done']

def test_queue_get_cancel():
    results = []
    def consumer(q):
        while True:
            try:
                item = q.get()
            except thredo.ThreadCancelled:
                results.append('cancel')
                raise
        
    def main():
        q = thredo.Queue()
        t = thredo.spawn(consumer, q)
        results.append('start')
        t.cancel()

    thredo.run(main)
    assert results == ['start', 'cancel']

def test_queue_put_cancel():
    results = []
    def producer(q):
        while True:
            try:
                q.put(True)
            except thredo.ThreadCancelled:
                results.append('cancel')
                raise
            
    def main():
        q = thredo.Queue(maxsize=1)
        t = thredo.spawn(producer, q)
        results.append('start')
        thredo.sleep(0.1)
        t.cancel()
    
    thredo.run(main)
    assert results == ['start', 'cancel']

def test_queue_join_cancel():
    results = []
    def producer(q):
        q.put(True)
        try:
            q.join()
        except thredo.ThreadCancelled:
            results.append('cancel')
            raise
            
    def main():
        q = thredo.Queue(maxsize=1)
        t = thredo.spawn(producer, q)
        results.append('start')
        thredo.sleep(0.1)
        t.cancel()
    
    thredo.run(main)
    assert results == ['start', 'cancel']

            



    

    
    


