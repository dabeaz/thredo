import thredo
import thredo.requests

def get(session, url):
    try:
        return session.get(url)
    except thredo.ThreadCancelled as e:
        print("Cancelled", url)

def main():
    s = thredo.requests.get_session()

    with thredo.ThreadGroup(wait=any) as g:
        g.spawn(get, s, 'http://www.dabeaz.com/cgi-bin/saas.py?s=5')
        g.spawn(get, s, 'http://www.dabeaz.com/cgi-bin/saas.py?s=10')
        g.spawn(get, s, 'http://www.dabeaz.com/cgi-bin/fib.py?n=10')

    print(g.completed.result.text)

if __name__ == '__main__':
    thredo.run(main)

