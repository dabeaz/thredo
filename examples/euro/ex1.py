import thredo

def func(x, y):
    return x + y
    
def main():
    t = thredo.spawn(func, 2, '3')
    try:
        print('Result:', t.join())
    except thredo.ThreadError as e:
        print('Failed:', repr(e.__cause__))
    
thredo.run(main)