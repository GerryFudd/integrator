from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction
from elementary_functions.utils import ConstantFunction
from custom_numbers.computation import Number
from custom_numbers.types import Numeric


class Circle:
    def __init__(self, a: Numeric, b: Numeric, r: Numeric):
        self.a = Number.of(a)
        self.b = Number.of(b)
        self.r = Number.of(r)
        self.func = PowerFunction(0.5) \
            @ Polynomial(self.r ** 2 - self.a ** 2, 2 * self.a, Number.of(-1)) \
            + ConstantFunction(b)

    def __repr__(self):
        return f'Circle(a={self.a}, b={self.b}, r={self.r})'

    def evaluate(self, x: Numeric) -> Numeric:
        return (self.r ** 2 - (Number.of(x) - self.a) ** 2) ** 0.5 + self.b
