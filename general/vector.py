from __future__ import annotations
from general.numbers import Numeric


class Vector:
    def __init__(self, *coefficients: Numeric):
        self.coefficients = list(coefficients)

    def __eq__(self, other):
        return self.coefficients == other.coefficients

    def __getitem__(self, item):
        return self.coefficients[item]

    def __iter__(self):
        return self.coefficients.__iter__()

    def __add__(self, other):
        result = []
        for index, coefficient in enumerate(self.coefficients):
            result.append(other[index] + coefficient)
        return Vector(*result)

    def __rmul__(self, other):
        return Vector(*map(lambda x: other * x, self.coefficients))

    def __neg__(self):
        return -1 * self
