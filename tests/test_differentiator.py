from calculus.differentiator import differentiate
from custom_numbers.exact.rational_number import RationalNumber
from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction
from elementary_functions.simple import CharacteristicFunction, SimpleFunction
from elementary_functions.calculus_utils import ConstantFunction
from general.interval import Interval


def test_differentiate_power():
    assert differentiate(PowerFunction(6, RationalNumber(-7, 3))) == \
        PowerFunction(5, -14)


def test_differentiate_power_sum():
    f = PowerFunction(6, RationalNumber(-7, 3))
    g = PowerFunction(5, RationalNumber(12, 5))
    assert differentiate(f + g) == \
        PowerFunction(5, -14) + PowerFunction(4, 12)


def test_differentiate_polynomial():
    assert differentiate(Polynomial(37, 24, 9, 6)) == Polynomial(24, 18, 18)


def test_differentiate_characteristic_function():
    assert differentiate(CharacteristicFunction(Interval(-12, 84), 37)) == \
           ConstantFunction()


def test_differentiate_simple_function():
    assert differentiate(SimpleFunction(
        CharacteristicFunction(Interval(-12, 84), 37),
        CharacteristicFunction(Interval(97, 114), -1),
    )) == ConstantFunction()

