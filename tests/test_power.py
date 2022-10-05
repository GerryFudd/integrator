from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction


def test_sum():
    assert PowerFunction(3, 2) + PowerFunction(4, -3) == \
           Polynomial(0, 0, 0, 2, -3)
