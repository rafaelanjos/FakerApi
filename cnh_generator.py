import random
from faker.providers import BaseProvider


def cnh():
    def n(): return random.randint(0, 9)
    r, t, e, a, o, c, u, i, m = n(), n(), n(), n(), n(), n(), n(), n(), n()

    primeiro_verificador = (r * 9 + t * 8 + e * 7 +
                            a * 6 + o * 5 + c * 4 + u * 3 + i * 2 + m) % 11
    if primeiro_verificador >= 10:
        v = 2
        primeiro_verificador = 0
    else:
        v = 0

    segundo_verificador = (r + t * 2 + e * 3 + a * 4 +
                           o * 5 + c * 6 + u * 7 + i * 8 + m * 9) % 11
    segundo_verificador = 0 if segundo_verificador >= 10 else segundo_verificador - v

    if segundo_verificador < 0:
        return cnh()

    return f"{r}{t}{e}{a}{o}{c}{u}{i}{m}{primeiro_verificador}{segundo_verificador}"


class CnhGenerator(BaseProvider):
    def cnh(self) -> str:
        return cnh()
