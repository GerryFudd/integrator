from typing import TypeVar, Callable

from custom_numbers.types import Numeric
from general.vector import Vector


ExpressionType = TypeVar('ExpressionType')
SolutionType = TypeVar('SolutionType')


class PolynomialExpression:
    def __init__(
        self, *coefficients: Numeric
    ):
        self.coefficients = Vector(*coefficients)

    @staticmethod
    def __term_str(i, c):
        if i == 0:
            return str(c)
        if i == 1:
            return f'{c}x'
        return f'{c}x^({i})'

    def __str__(self):
        return ' + '.join(map(
            self.__term_str,
            filter(lambda i, x: x != 0, enumerate(self.coefficients))
        ))

    def __repr__(self):
        return f'PolynomialExpression({", ".join(map(str, self.coefficients))})'

    def __getitem__(self, item):
        return self.coefficients[item]

    def to_type(
        self, map_to_type: Callable[[Numeric], Numeric] = lambda x: x,
    ):
        return PolynomialExpression(*map(map_to_type, self.coefficients))

    def __eq__(self, other):
        return self.coefficients == other.coefficients

    def __ne__(self, other):
        return not (self == other)

    def __len__(self):
        return len(self.coefficients.coefficients)

    def __add__(self, other):
        if isinstance(other, Numeric):
            return self + PolynomialExpression(other)
        if isinstance(other, PolynomialExpression):
            return PolynomialExpression(*(
                self.coefficients + other.coefficients
            ))
        raise NotImplementedError

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if isinstance(other, Numeric):
            return PolynomialExpression(*(other * self.coefficients))
        raise NotImplementedError

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, Numeric):
            return PolynomialExpression(*(self.coefficients / other))
        raise NotImplementedError

    def __neg__(self):
        return PolynomialExpression(*(-self.coefficients))
