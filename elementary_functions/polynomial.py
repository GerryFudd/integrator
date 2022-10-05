from typing import List

from calculus.utils import maximum
from elementary_functions.utils import FunctionSum, Function
from elementary_functions.power import PowerFunction
from general.numbers import Numeric


class Polynomial:
    def __init__(self, *coefficients):
        self.coefficients = list(coefficients)
        func = FunctionSum()
        for power, coefficient in enumerate(self.coefficients):
            if not coefficient == 0:
                func += PowerFunction(power, coefficient)
        self.func = func

    def __eq__(self, other):
        if isinstance(other, FunctionSum):
            return other == self
        if not isinstance(other, Polynomial):
            return False
        return self.coefficients == other.coefficients

    def __str__(self):
        return str(self.func)

    def __repr__(self):
        return f'Polynomial(coefficients={self.coefficients})'

    def __reduce(self):
        while self.coefficients[-1] == 0:
            self.coefficients.pop()
        return self

    def __rmul__(self, other):
        return Polynomial(*map(lambda x: other * x, self.coefficients))

    def __add__(self, other):
        if isinstance(other, Polynomial):
            coefficients = []
            for n in range(maximum(
                len(self.coefficients), len(other.coefficients)
            )):
                if n >= len(self.coefficients):
                    coefficients.append(other.coefficients[n])
                elif n >= len(other.coefficients):
                    coefficients.append(self.coefficients[n])
                else:
                    coefficients.append(
                        self.coefficients[n] + other.coefficients[n]
                    )
            return Polynomial(*coefficients).__reduce()
        return FunctionSum(self, other)

    def __mul__(self, other):
        if not isinstance(other, Polynomial):
            raise NotImplementedError
        self.__reduce()
        other.__reduce()
        coefficients = []
        for n in range(len(self.coefficients)):
            for m in range(len(other.coefficients)):
                i = n + m
                if i < len(coefficients):
                    coefficients[i] = coefficients[i] \
                                      + self.coefficients[n] \
                                      * other.coefficients[m]
                else:
                    coefficients.insert(
                        i, self.coefficients[n] * other.coefficients[m]
                    )
        return Polynomial(*coefficients)

    @property
    def constituents(self) -> List[Function]:
        return self.func.constituents

    def evaluate(self, x: Numeric) -> Numeric:
        return self.func.evaluate(x)
