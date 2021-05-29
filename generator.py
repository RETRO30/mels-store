import random


def generate(len_):
    return ''.join([str(random.randint(0, 9)) for _ in range(len_)])
