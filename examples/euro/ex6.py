# Example 6 - Queues

import thredo

def worker(q, label):
    try:
        while True:
            item = q.get()
            print(label, item)
            q.task_done()
    except thredo.ThreadCancelled:
        print("Cancelled", label)
        
def spin(n):
    while n > 0:
        n -= 1
        if n % 10_000_000 == 0:
            print('spin', n)
            
def main():
#    thredo.spawn(spin, 60_000_000)
    q = thredo.Queue()
    with thredo.ThreadGroup(wait=None) as g:
        g.spawn(spin,100_000_000)
        for n in range(4):
            g.spawn(worker, q, f'Worker-{n}')
            
        for n in range(10):
            q.put(n)
            thredo.sleep(1)
            
        q.join()
        
    print('Done')
    
thredo.run(main)