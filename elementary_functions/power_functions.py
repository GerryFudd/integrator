from general.utils import Numeric


class PowerFunction:
    def __init__(self, power: int):
        self.power = power

    def __str__(self):
        if self.power == 0:
            return '1'
        if self.power == 1:
            return 'x'
        if self.power >= 10:
            return f'x^({self.power})'
        return f'x^{self.power}'

    def evaluate(self, x: Numeric) -> Numeric:
        result = 1
        for factor in [x] * abs(self.power):
            if self.power >= 0:
                result *= factor
            else:
                result /= factor
        return result
