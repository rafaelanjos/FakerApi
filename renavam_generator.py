import random
#from faker import Faker
from faker.providers import BaseProvider


def generate_random(nuns):
    return [random.randint(0, 8) for _ in range(nuns)]


def renavam_onze(mask):
    nums = generate_random(10)

    modulo_onze = sum(nums[i] * (3 - i if i < 2 else 9 - i)
                      for i in range(10)) * 10 % 11
    modulo_onze = 0 if modulo_onze == 10 else modulo_onze

    if mask:
        return f"{''.join(map(str, nums))}-{modulo_onze}"
    else:
        return f"{''.join(map(str, nums))}{modulo_onze}"


def renavam_nove(mask):
    nums = generate_random(8)

    modulo_nove = sum(nums[i] * (9 - i) for i in range(8)) * 8 % 9

    if mask:
        return f"{''.join(map(str, nums))}-{modulo_nove}"
    else:
        return f"{''.join(map(str, nums))}{modulo_nove}"


def renavam(onze, mask):
    if onze:
        return renavam_onze(mask)
    else:
        return renavam_nove(mask)


class RenavamGenerator(BaseProvider):
    def renavam(self, onze, mask) -> str:
        return renavam(onze, mask)
