import thredo

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print("Child:", item)
        thredo.sleep(0.01)
        

def producer(q, count):
    for n in range(count):
        q.put(n)
        print("Produced:", n)
    q.put(None)

def main():
    q = thredo.Queue(maxsize=1)
    t1 = thredo.spawn(consumer, q)
    t2 = thredo.spawn(producer, q, 1000)
    t1.join()
    t2.join()

thredo.run(main)


