import random


def coin_flip():
    return random.getrandbits(1) == 0


def random_variance(mid, var):
    return mid - var + sum_of_n_coin_flips(var * 2)


def sum_of_n_coin_flips(n):
    result = 0
    for _ in range(n):
        if coin_flip():
            result += 1
    return result


def random_variance_no_negative(mid, var):
    result = random_variance(mid, var)
    return max(result, 0)
