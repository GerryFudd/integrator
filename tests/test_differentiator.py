from calculus.differentiator import differentiate
from elementary_functions.power import PowerFunction
from general.numbers import RationalNumber


def test_differentiate_power():
    assert differentiate(PowerFunction(6, RationalNumber(-7, 3))) == \
        PowerFunction(5, -14)


def test_differentiate_power_sum():
    f = PowerFunction(6, RationalNumber(-7, 3))
    g = PowerFunction(5, RationalNumber(12, 5))
    assert differentiate(f + g) == \
        PowerFunction(5, -14) + PowerFunction(4, 12)
