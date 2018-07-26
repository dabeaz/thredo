# Example 2: Real threads

import thredo

def func(n, label):
    total = 0
    while n > 0:
        total += n
        n -= 1
        if n % 10_000_000 == 0:
            print(label, n)
    return total
    
def main():
    t1 = thredo.spawn(func, 60_000_000, 'thread-1')
    t2 = thredo.spawn(func, 40_000_000, 'thread-2')
    print(t1.join())
    print(t2.join())

thredo.run(main)