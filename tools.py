import time

__author__ = 'co'


def time_it(name, func):
    start = time.clock()
    result = func()
    elapsed = time.clock() - start
    print name + ": " + str(elapsed)
    return result