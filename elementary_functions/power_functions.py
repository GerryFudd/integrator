from elementary_functions.utils import FunctionSum
from general.utils import Numeric, RationalNumber


class PowerFunction:
    def __init__(self, power: Numeric, coefficient: Numeric = 1):
        self.power = power
        self.coefficient = coefficient

    def __str__(self):
        if self.power == 0:
            return str(self.coefficient)
        if self.power == 1:
            return f'{self.coefficient}x'
        if self.power in [x - 9 for x in range(19)]:
            return f'{self.coefficient}x^{self.power}'
        return f'{self.coefficient}x^({self.power})'

    def evaluate(self, x: Numeric) -> Numeric:
        return (RationalNumber.resolve(x) ** self.power) * self.coefficient

    def __rmul__(self, other):
        return PowerFunction(self.power, self.coefficient * other)

    def __add__(self, other):
        if isinstance(other, PowerFunction) and self.power == other.power:
            return PowerFunction(
                self.power,
                self.coefficient + other.coefficient
            )
        return FunctionSum(self, other)
