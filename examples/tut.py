import threadio
import signal

def countdown(n):
    while n > 0:
        print('T-minus', n)
        threadio.sleep(1)
        n -= 1

def friend(name):
    print('Hi, my name is', name)
    print('Playing Minecraft')
    try:
        threadio.sleep(1000)
    except threadio.CancelledError:
        print(name, 'going home')
        raise

start_evt = threadio.Event()

def kid():
    while True:
        try:
            print('Can I play?')
            threadio.timeout_after(1, start_evt.wait)
            break
        except threadio.ThreadTimeout:
            print('Wha!?!')

    print('Building the Millenium Falcon in Minecraft')
    with threadio.ThreadGroup() as f:
        f.spawn(friend, 'Max')
        f.spawn(friend, 'Lillian')
        f.spawn(friend, 'Thomas')
        try:
            threadio.sleep(1000)
        except threadio.CancelledError:
            print('Fine. Saving my work.')
            raise

def parent():
    goodbye = threadio.SignalEvent(signal.SIGINT, signal.SIGTERM)

    kid_task = threadio.spawn(kid)
    threadio.sleep(5)
    print("Yes, go play")
    start_evt.set()

    goodbye.wait()
    del goodbye

    print("Let's go")
    count_task = threadio.spawn(countdown, 10)
    count_task.join()

    print("We're leaving!")
    try:
        threadio.timeout_after(10, kid_task.join)
    except threadio.ThreadTimeout:
        kid_task.cancel()
        threadio.sleep(3)
    print('Parent Leaving')

if __name__ == '__main__':
    threadio.run(parent)
