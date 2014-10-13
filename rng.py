import random


def coin_flip():
    return random.getrandbits(1) == 0


def random_variance(mid, var):
    if var == 0:
        return mid
    else:
        return mid - var + random.randrange(var + 1) + random.randrange(var + 1)


def sum_of_n_coin_flips(n):
    result = 0
    for _ in range(n):
        if coin_flip():
            result += 1
    return result


def random_variance_no_negative(mid, var):
    result = random_variance(mid, var)
    return max(result, 0)


def stat_check(stat1, stat2):
    """
    Checks if stat1 wins over stat2 in competitive stat check.
    """
    roll1 = random.randrange(stat1)
    roll2 = random.randrange(stat2)
    return roll1 >= roll2


def weighted_choice(options, weight_function=(lambda option: option.weight)):
    total = sum(weight_function(option) for option in options)
    random_choice = random.uniform(0, total)
    upto = 0
    for option in options:
        weight = weight_function(option)
        if upto + weight > random_choice:
            return option
        upto += weight
    raise Exception("Weighted choice error.")
