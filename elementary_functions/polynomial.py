from typing import List

from custom_numbers.types import Numeric
from custom_numbers.utils import maximum
from elementary_functions.calculus_utils import ConstantFunction, \
    DifferentiableSum, DifferentiableFunction
from elementary_functions.power import PowerFunction
from elementary_functions.utils import FunctionSum, CompositeFunction


class Polynomial(DifferentiableSum):
    constituents: List[PowerFunction]

    def __init__(self, *coefficients: Numeric):
        self.coefficients = list(coefficients)
        DifferentiableSum.__init__(self, *filter(
            lambda x: x.coefficient != 0,
            map(
                lambda x: PowerFunction(x[0], x[1]),
                enumerate(self.coefficients),
            )
        ))

    def __eq__(self, other):
        if isinstance(other, FunctionSum):
            return set(self.constituents) == set(other.constituents)
        return len(self.constituents) == 1 and self.constituents[0] == other

    def __req__(self, other):
        if isinstance(other, PowerFunction):
            return self == other
        raise NotImplementedError

    def __repr__(self):
        return f'Polynomial(coefficients={self.coefficients})'

    def __reduce(self):
        while self.coefficients[-1] == 0:
            self.coefficients.pop()
        return Polynomial(*self.coefficients)

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

    def __matmul__(self, other):
        if isinstance(other, Polynomial) or isinstance(other, PowerFunction):
            term = Polynomial(1)
            result = ConstantFunction()
            for coefficient in self.coefficients:
                result += coefficient * term
                term *= other
            return result
        return CompositeFunction(self, other)

    def differentiate(self) -> DifferentiableFunction:
        return Polynomial(*map(
            lambda x: (x[0] + 1) * x[1],
            enumerate(self.coefficients[1:])
        ))
