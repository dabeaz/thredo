import threadio

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print("Child:", item)
        threadio.sleep(0.01)
        

def producer(q, count):
    for n in range(count):
        q.put(n)
        print("Produced:", n)
    q.put(None)

def main():
    q = threadio.Queue(maxsize=1)
    t1 = threadio.spawn(consumer, q)
    t2 = threadio.spawn(producer, q, 1000)
    t1.join()
    t2.join()

threadio.run(main)


