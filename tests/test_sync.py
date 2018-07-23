import thredo

def test_event_wait():
    evt = thredo.Event()
    result = []
    def waiter():
        evt.wait()
        result.append('waiter')
        
    def main():
        t = thredo.spawn(waiter)
        result.append('start')
        evt.set()
        t.join()
        
    thredo.run(main)
    assert result == ['start', 'waiter']
    evt.clear()
    assert not evt.is_set() 

def test_event_wait_cancel():
    evt = thredo.Event()
    result = []
    def waiter():
        try:
            evt.wait()
            result.append('waiter')
        except thredo.ThreadCancelled:
            result.append('cancel')
        
    def main():
        t = thredo.spawn(waiter)
        result.append('start')
        t.cancel()
        
    thredo.run(main)
    assert result == ['start', 'cancel']

def test_lock():
    lock = thredo.Lock()
    result = []
    def child():
        with lock:
            result.append('child')
            
            
    def main():
        lock.acquire()
        if lock.locked():
            result.append('locked')
        try:
            t = thredo.spawn(child)
            result.append('parent')
        finally:
            lock.release()
        t.join()

    thredo.run(main)
    assert result == ['locked', 'parent', 'child']

def test_lock_cancel():
    lock = thredo.Lock()
    result = []
    def child():
        try:
            with lock:
                result.append('child')
        except thredo.ThreadCancelled:
            result.append('cancel')
            
    def main():
        lock.acquire()
        try:
            t = thredo.spawn(child)
            result.append('parent')
            t.cancel()
        finally:
            lock.release()

    thredo.run(main)
    assert result == ['parent', 'cancel']

def test_lock_race():
    lock = thredo.Lock()
    evt = thredo.Event()
    n = 0
    def incr(count):
        nonlocal n
        evt.wait()
        while count > 0:
            with lock:
                n += 1
            count -=1
            
    def decr(count):
        nonlocal n
        evt.wait()
        while count > 0:
            with lock:
                n -= 1
            count -= 1

    def main():
        t1 = thredo.spawn(incr, 10000)
        t2 = thredo.spawn(decr, 10000)
        evt.set()
        t1.join()
        t2.join()

    thredo.run(main)
    assert n == 0

def test_semaphore():
    lock = thredo.Semaphore()
    result = []
    def child():
        with lock:
            result.append('child')
            
            
    def main():
        lock.acquire()
        result.append(lock.value)
        try:
            t = thredo.spawn(child)
            result.append('parent')
        finally:
            lock.release()
        t.join()

    thredo.run(main)
    assert result == [0, 'parent', 'child']

def test_semaphore_cancel():
    lock = thredo.Semaphore()
    result = []
    def child():
        try:
            with lock:
                result.append('child')
        except thredo.ThreadCancelled:
            result.append('cancel')
            
    def main():
        lock.acquire()
        try:
            t = thredo.spawn(child)
            result.append('parent')
            t.cancel()
        finally:
            lock.release()

    thredo.run(main)
    assert result == ['parent', 'cancel']

def test_semaphore_race():
    lock = thredo.Semaphore()
    evt = thredo.Event()
    n = 0
    def incr(count):
        nonlocal n
        evt.wait()
        while count > 0:
            with lock:
                n += 1
            count -=1
            
    def decr(count):
        nonlocal n
        evt.wait()
        while count > 0:
            with lock:
                n -= 1
            count -= 1

    def main():
        t1 = thredo.spawn(incr, 10000)
        t2 = thredo.spawn(decr, 10000)
        evt.set()
        t1.join()
        t2.join()

    thredo.run(main)
    assert n == 0


def test_rlock():
    lock = thredo.RLock()
    result = []
    def child():
        with lock:
            result.append('child')
            
            
    def main():
        lock.acquire()
        if lock.locked():
            result.append('locked')
        try:
            t = thredo.spawn(child)
            result.append('parent')
        finally:
            lock.release()
        t.join()

    thredo.run(main)
    assert result == ['locked', 'parent', 'child']

def test_rlock_cancel():
    lock = thredo.RLock()
    result = []
    def child():
        try:
            with lock:
                result.append('child')
        except thredo.ThreadCancelled:
            result.append('cancel')
            
    def main():
        lock.acquire()
        try:
            t = thredo.spawn(child)
            result.append('parent')
            t.cancel()
        finally:
            lock.release()

    thredo.run(main)
    assert result == ['parent', 'cancel']

def test_rlock_race():
    lock = thredo.RLock()
    evt = thredo.Event()
    n = 0
    def incr(count):
        nonlocal n
        evt.wait()
        while count > 0:
            with lock:
                n += 1
            count -=1
            
    def decr(count):
        nonlocal n
        evt.wait()
        while count > 0:
            with lock:
                n -= 1
            count -= 1

    def main():
        t1 = thredo.spawn(incr, 10000)
        t2 = thredo.spawn(decr, 10000)
        evt.set()
        t1.join()
        t2.join()

    thredo.run(main)
    assert n == 0



def test_condition():
    lock = thredo.Condition()
    result = []
    def child():
        with lock:
            result.append('child')
            
            
    def main():
        lock.acquire()
        if lock.locked():
            result.append('locked')
        try:
            t = thredo.spawn(child)
            result.append('parent')
        finally:
            lock.release()
        t.join()

    thredo.run(main)
    assert result == ['locked', 'parent', 'child']

def test_condition_cancel():
    lock = thredo.Condition()
    result = []
    def child():
        try:
            with lock:
                result.append('child')
        except thredo.ThreadCancelled:
            result.append('cancel')
            
    def main():
        lock.acquire()
        try:
            t = thredo.spawn(child)
            result.append('parent')
            t.cancel()
        finally:
            lock.release()

    thredo.run(main)
    assert result == ['parent', 'cancel']

def test_condition_race():
    lock = thredo.Condition()
    evt = thredo.Event()
    n = 0
    def incr(count):
        nonlocal n
        evt.wait()
        while count > 0:
            with lock:
                n += 1
            count -=1
            
    def decr(count):
        nonlocal n
        evt.wait()
        while count > 0:
            with lock:
                n -= 1
            count -= 1

    def main():
        t1 = thredo.spawn(incr, 10000)
        t2 = thredo.spawn(decr, 10000)
        evt.set()
        t1.join()
        t2.join()

    thredo.run(main)
    assert n == 0

def test_condition_wait_notify():
    n = 0
    lock = thredo.Condition(thredo.Lock())
    result = []
    def waiter():
        current = n
        while True:
            with lock:
                while current == n:
                    lock.wait()
                result.append(('consume', n))
                current = n
            if n >= 5:
                break

    def producer():
        nonlocal n
        while n < 5:
            thredo.sleep(0.1)
            with lock:
                n += 1
                result.append(('produce', n))
                lock.notify()
        

    def main():
        t1 = thredo.spawn(waiter)
        t2 = thredo.spawn(producer)
        t1.join()
        t2.join()

    thredo.run(main)
    assert result == [('produce',1), ('consume',1),
                     ('produce',2), ('consume',2),
                     ('produce',3), ('consume',3),
                     ('produce',4), ('consume',4),
                     ('produce',5), ('consume',5)]
            
        


        

    
