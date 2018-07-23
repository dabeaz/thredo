import threadio
import threadio.requests

def get(session, url):
    try:
        return session.get(url)
    except threadio.ThreadCancelled as e:
        print("Cancelled", url)

def main():
    s = threadio.requests.get_session()

    with threadio.ThreadGroup(wait=any) as g:
        g.spawn(get, s, 'http://www.dabeaz.com/cgi-bin/saas.py?s=5')
        g.spawn(get, s, 'http://www.dabeaz.com/cgi-bin/saas.py?s=10')
        g.spawn(get, s, 'http://www.dabeaz.com/cgi-bin/fib.py?n=10')

    print(g.completed.result.text)

if __name__ == '__main__':
    threadio.run(main)

