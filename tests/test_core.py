# test_core.py
#
# Tests for core functions and threads

import thredo
import time

def basic_thread(x, y):
    return x + y


def test_good():
    result = thredo.run(basic_thread, 2, 2)
    assert result == 4

def test_bad():
    try:
        result = thredo.run(basic_thread, 2, '2')
        assert False
    except BaseException as e:
        assert type(e) == TypeError

def test_good_spawn():
    result = []
    def main():
        t = thredo.spawn(basic_thread, 2, 2)
        result.append(t.join())
        
    thredo.run(main)
    assert result == [4]

def test_bad_spawn():
    result = []
    def main():
        t = thredo.spawn(basic_thread, 2, '2')
        try:
            t.join()
        except thredo.ThreadError as e:
            result.append('error')
            result.append(type(e.__cause__))

    thredo.run(main)
    assert result == ['error', TypeError]

def test_sleep():
    result = []
    def main():
        start = time.time()
        thredo.sleep(1.0)
        end = time.time()
        result.append(end-start)
        
    thredo.run(main)
    assert result[0] > 1.0

def test_sleep_cancel():
    result = []
    def child():
        try:
            thredo.sleep(10)
        except thredo.ThreadCancelled:
            result.append('cancel')

    def main():
        t = thredo.spawn(child)
        thredo.sleep(0.1)
        t.cancel()

    thredo.run(main)
    assert result == ['cancel']

def test_timeout():
    result = []
    def main():
        try:
            thredo.timeout_after(0.25, thredo.sleep, 1)
        except thredo.ThreadTimeout:
            result.append('timeout')
            
    thredo.run(main)
    assert result == ['timeout']

def test_timeout_context():
    result = []
    def main():
        try:
            with thredo.timeout_after(0.25):
                thredo.sleep(1)
        except thredo.ThreadTimeout:
            result.append('timeout')
            
    thredo.run(main)
    assert result == ['timeout']

def test_ignore():
    def main():
        thredo.ignore_after(0.25, thredo.sleep, 1)

    start = time.time()
    thredo.run(main)
    end = time.time()
    assert (end-start) < 1

def test_ignore_context():
    def main():
        with thredo.ignore_after(0.25):
            thredo.sleep(1)

    start = time.time()
    thredo.run(main)
    end = time.time()
    assert (end-start) < 1
