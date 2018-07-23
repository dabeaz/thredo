# Example 2
#
# Launching multiple CPU-bound threads and collecting their results

import thredo

def sum_to_n(n, label):
    total = 0
    while n > 0:
        total += n
        n -= 1
        if n % 10000000 == 0:
            print(label, n)
    return total

def main():
    t1 = thredo.spawn(sum_to_n, 50_000_000, 'thread 1')
    t2 = thredo.spawn(sum_to_n, 30_000_000, 'thread 2')
    print('Result 1:', t1.join())
    print('Result 2:', t2.join())

thredo.run(main)
