# Example 1
#
# Launching a thread and collecting its result

import thredo

def func(x, y):
    return x + y

def main():
    t = thredo.spawn(func, 2, 3)
    result = t.join()
    print('Result:', result)

thredo.run(main)
