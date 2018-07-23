# Example 3
#
# Cancelling a thread

import thredo

def hello(sec):
    print("Yawn")
    try:
        thredo.sleep(sec)
        print("Awake")
    except thredo.ThreadCancelled:
        print("Cancelled!")

def main():
    t = thredo.spawn(hello, 100)
    thredo.sleep(5)
    t.cancel()
    print("Goodbye")

thredo.run(main)
