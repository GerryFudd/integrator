from typing import List

from calculus.utils import maximum
from elementary_functions.utils import FunctionSum, Function, ConstantFunction, \
    CompositeFunction
from elementary_functions.power import PowerFunction
from general.numbers import Numeric


class Polynomial:
    def __init__(self, *coefficients: Numeric):
        self.coefficients = list(coefficients)
        func = FunctionSum()
        for power, coefficient in enumerate(self.coefficients):
            if not coefficient == 0:
                func += PowerFunction(power, coefficient)
        self.func = func

    def __eq__(self, other):
        if isinstance(other, ConstantFunction):
            return self.coefficients == [other.val]
        if isinstance(other, PowerFunction):
            return other.power == len(self.coefficients) - 1 \
                   and isinstance(other.power, int) \
                   and self.coefficients[:-1] == [0] * other.power \
                   and self.coefficients[other.power] == other.coefficient
        if isinstance(other, FunctionSum):
            return other == self
        if not isinstance(other, Polynomial):
            return False
        return self.coefficients == other.coefficients

    def __req__(self, other):
        if isinstance(other, PowerFunction):
            return self == other
        raise NotImplementedError

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

    def __matmul__(self, other):
        if isinstance(other, Polynomial) or isinstance(other, PowerFunction):
            term = Polynomial(1)
            result = ConstantFunction()
            for coefficient in self.coefficients:
                result += coefficient * term
                term *= other
            return result
        return CompositeFunction(self, other)

    @property
    def constituents(self) -> List[Function]:
        return self.func.constituents

    def evaluate(self, x: Numeric) -> Numeric:
        return self.func.evaluate(x)
