import time

__author__ = 'co'


def time_it(name, func):
    start = time.clock()
    result = func()
    elapsed = time.clock() - start
    print name + ": " + str(elapsed)
    return result


def time_it_return_time(func):
    start = time.clock()
    func()
    return time.clock() - start
