from decimal import Decimal

from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction
from elementary_functions.utils import ConstantFunction
from general.numbers import Numeric


class Circle:
    def __init__(self, a: Numeric, b: Numeric, r: Numeric):
        self.func = PowerFunction(0.5) \
                    @ Polynomial(r ** 2 - a ** 2, 2 * a, -1) \
                    + ConstantFunction(b)
        self.a = Decimal(str(a))
        self.b = Decimal(str(b))
        self.r = Decimal(str(r))

    def __repr__(self):
        return f'Circle(a={self.a}, b={self.b}, r={self.r})'

    def evaluate(self, x: Numeric) -> Numeric:
        return (
                   self.r ** 2
                   - (Decimal(str(x)) - self.a) ** 2
               ) ** Decimal('0.5') + self.b
