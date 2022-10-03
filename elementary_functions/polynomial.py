from typing import List

from calculus.utils import maximum
from elementary_functions.utils import FunctionSum, Function
from elementary_functions.power_functions import PowerFunction
from general.utils import Numeric


class Polynomial:
    def __init__(self, *coefficients):
        self.coefficients = list(coefficients)
        terms = []
        for power, coefficient in enumerate(self.coefficients):
            if not coefficient == 0:
                terms.append(PowerFunction(power, coefficient))
        self.func = FunctionSum(*terms)

    def __eq__(self, other):
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

    def plus(self, summand):
        coefficients = []
        for n in range(maximum(
            len(self.coefficients), len(summand.coefficients)
        )):
            if n >= len(self.coefficients):
                coefficients.append(summand.coefficients[n])
            elif n >= len(summand.coefficients):
                coefficients.append(self.coefficients[n])
            else:
                coefficients.append(
                    self.coefficients[n] + summand.coefficients[n]
                )
        return Polynomial(*coefficients).__reduce()

    def times(self, multiplicand):
        self.__reduce()
        multiplicand.__reduce()
        coefficients = []
        for n in range(len(self.coefficients)):
            for m in range(len(multiplicand.coefficients)):
                i = n + m
                if i < len(coefficients):
                    coefficients[i] = coefficients[i] \
                                      + self.coefficients[n] \
                                      * multiplicand.coefficients[m]
                else:
                    coefficients.insert(
                        i, self.coefficients[n] * multiplicand.coefficients[m]
                    )
        return Polynomial(*coefficients)

    @property
    def constituents(self) -> List[Function]:
        return self.func.constituents

    def evaluate(self, x: Numeric) -> Numeric:
        return self.func.evaluate(x)
