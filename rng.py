import random


def coin_flip():
    return random.getrandbits(1) == 0


def random_variance(mid, var):
    result = mid - var
    for _ in range(var * 2):
        if coin_flip():
            result += 1
    return result


def random_variance_no_negative(mid, var):
    result = random_variance(mid, var)
    return max(result, 0)
