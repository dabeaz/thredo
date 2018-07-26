# Example : Cancellation with locks

import thredo

def func(lck, label):
    print(label, 'starting')
    with lck:
        print(label, 'working')
        thredo.sleep(5)
        print(label, 'done')
        
def main():
    lck = thredo.Semaphore()
    t1 = thredo.spawn(func, lck, 'thread-1')
    t2 = thredo.spawn(func, lck, 'thread-2')
    # Case 2: Cancel a thread holding a lock
    thredo.sleep(2)
    t1.cancel()
    t2.join()
#    t2.join()
    
thredo.run(main)

    