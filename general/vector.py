from __future__ import annotations
from custom_numbers.types import Numeric
from custom_numbers.utils import maximum


class Vector:
    def __init__(self, *coefficients: Numeric):
        self.coefficients = list(coefficients)

    def __str__(self):
        return f'<{",".join(map(str, self.coefficients))}>'

    def __repr__(self):
        return f'Vector({",".join(map(str, self.coefficients))})'

    def __eq__(self, other):
        return self.coefficients == other.coefficients

    def __getitem__(self, item):
        if item >= len(self.coefficients):
            return 0
        return self.coefficients[item]

    def __iter__(self):
        return self.coefficients.__iter__()

    def __add__(self, other):
        result = []
        for index in range(maximum(len(self), len(other))):
            result.append(self[index] + other[index])
        return Vector(*result)

    def __rmul__(self, other):
        return Vector(*map(lambda x: other * x, self.coefficients))

    def __truediv__(self, other):
        return Vector(*map(lambda x: x / other, self.coefficients))

    def __neg__(self):
        return -1 * self

    def __len__(self):
        return len(self.coefficients)
