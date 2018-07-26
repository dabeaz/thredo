# example 3: Cancellation

import thredo

def func():
    print('Yawn')
    try:
        thredo.sleep(10)
        print('Awake')
    except thredo.ThreadCancelled:
        print('Cancelled')
        

def main():
    t = thredo.spawn(func)
    thredo.sleep(2)
    t.cancel()
    #t.wait()
    
thredo.run(main)