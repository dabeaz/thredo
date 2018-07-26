# ex5.py

import thredo
import random

sticks = [thredo.Lock() for n in range(5)]

def philosopher(n):
    thredo.sleep(random.random())
    try:
        with sticks[n]:
            thredo.sleep(random.random())
            with sticks[(n+1) % 5]:
                print("eating", n)
                thredo.sleep(random.random())
    except thredo.ThreadCancelled:
        print(f"But what is death? {n}")

def main():
    phils = [ thredo.spawn(philosopher, n) for n in range(5) ]
    try:
        with thredo.timeout_after(10):
            for p in phils:
                p.wait()
    except thredo.ThreadTimeout:
        phils[random.randint(0,4)].cancel()
        for p in phils:
            p.wait()
            
        
thredo.run(main)