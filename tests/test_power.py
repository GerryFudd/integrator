from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction
from elementary_functions.utils import ConstantFunction


def test_sum():
    assert PowerFunction(3, 2) + PowerFunction(4, -3) == \
           Polynomial(0, 0, 0, 2, -3)


def test_equals_constant():
    assert PowerFunction(0, 3) == ConstantFunction(3)
    assert ConstantFunction(3) == PowerFunction(0, 3)


def test_equals_constant_polynomial():
    assert PowerFunction(0, 3) == Polynomial(3)
    assert Polynomial(3) == PowerFunction(0, 3)


def test_equals_linear_polynomial():
    assert PowerFunction(1, 3) == Polynomial(0, 3)
    assert Polynomial(0, 3) == PowerFunction(1, 3)


def test_equals_higher_order_polynomial():
    assert PowerFunction(7, 3) == Polynomial(0, 0, 0, 0, 0, 0, 0, 3)
    assert Polynomial(0, 0, 0, 0, 0, 0, 0, 3) == PowerFunction(7, 3)
