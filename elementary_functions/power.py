from elementary_functions.utils import FunctionSum
from general.numbers import Numeric, RationalNumber


class PowerFunction:
    def __init__(self, power: Numeric, coefficient: Numeric = 1):
        self.power = power
        self.coefficient = coefficient

    def __repr__(self):
        return f'PowerFunction(power={self.power},coefficient=' \
               f'{self.coefficient})'

    def __eq__(self, other):
        return isinstance(other, PowerFunction) \
           and self.power == other.power \
           and self.coefficient == other.coefficient

    def __hash__(self):
        return hash((self.coefficient, self.power, 'PowerFunction'))

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
