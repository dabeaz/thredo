# Example : Die Requests
#
# Note: This requests the serv.py program to be running in the background

import thredo

with thredo.more_magic():
    import requests
    
def func():
    try:
        r = requests.get('http://localhost:8000')
        return r.text
    except thredo.ThreadCancelled:
        print("Cancelled")
        
def main():
    with thredo.ThreadGroup(wait=any) as g:
        for n in range(4):
            g.spawn(func)
    print('Result:', g.completed.result)
        
thredo.run(main)
