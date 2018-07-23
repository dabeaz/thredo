import thredo
import signal

def countdown(n):
    while n > 0:
        print('T-minus', n)
        thredo.sleep(1)
        n -= 1

def friend(name):
    print('Hi, my name is', name)
    print('Playing Minecraft')
    try:
        thredo.sleep(1000)
    except thredo.CancelledError:
        print(name, 'going home')
        raise

start_evt = thredo.Event()

def kid():
    while True:
        try:
            print('Can I play?')
            thredo.timeout_after(1, start_evt.wait)
            break
        except thredo.ThreadTimeout:
            print('Wha!?!')

    print('Building the Millenium Falcon in Minecraft')
    with thredo.ThreadGroup() as f:
        f.spawn(friend, 'Max')
        f.spawn(friend, 'Lillian')
        f.spawn(friend, 'Thomas')
        try:
            thredo.sleep(1000)
        except thredo.CancelledError:
            print('Fine. Saving my work.')
            raise

def parent():
    goodbye = thredo.SignalEvent(signal.SIGINT, signal.SIGTERM)

    kid_task = thredo.spawn(kid)
    thredo.sleep(5)
    print("Yes, go play")
    start_evt.set()

    goodbye.wait()
    del goodbye

    print("Let's go")
    count_task = thredo.spawn(countdown, 10)
    count_task.join()

    print("We're leaving!")
    try:
        thredo.timeout_after(10, kid_task.join)
    except thredo.ThreadTimeout:
        kid_task.cancel()
        thredo.sleep(3)
    print('Parent Leaving')

if __name__ == '__main__':
    thredo.run(parent)
