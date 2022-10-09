from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction
from elementary_functions.utils import ConstantFunction
from custom_numbers.types import Numeric, ComputationType


class Circle:
    def __init__(self, a: Numeric, b: Numeric, r: Numeric):
        self.a = a
        self.b = b
        self.r = r
        self.func = PowerFunction(0.5) \
            @ Polynomial(self.r ** 2 - self.a ** 2, 2 * self.a, -1) \
            + ConstantFunction(b)

    def __repr__(self):
        return f'Circle(a={self.a}, b={self.b}, r={self.r})'

    def evaluate(self, x: ComputationType) -> ComputationType:
        return (self.r ** 2 - (x - self.a) ** 2) ** 0.5 + self.b
