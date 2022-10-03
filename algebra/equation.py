from abc import abstractmethod
from typing import Protocol, runtime_checkable

from general.numbers import Numeric
from general.vector import Vector


@runtime_checkable
class Equation(Protocol):
    @abstractmethod
    def solve(self) -> Numeric:
        raise NotImplementedError


class PolynomialExpression:
    def __init__(self, *coefficients: Numeric):
        self.coefficients = Vector(*coefficients)

    def __getitem__(self, item):
        return self.coefficients[item]

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
            return (1/other) * self
        raise NotImplementedError


class LinearEquation:
    def __init__(self, left: PolynomialExpression, right: PolynomialExpression):
        if len(left) != 2 or len(right) != 2:
            raise NotImplementedError
        self.left = left
        self.right = right

    def solve(self) -> Numeric:
        while self.left != PolynomialExpression(0, 1) or self.right[1] != 0:
            if self.left[1] == self.right[1] == 0:
                raise NotImplementedError
            if self.left[0] != 0:
                summand = PolynomialExpression(-self.left[0], -self.right[1])
                self.left += summand
                self.right += summand
                continue
            if self.left[1] != 1:
                divisor = self.left[1]
                self.left /= divisor
                self.right /= divisor
                continue
        return self.right[0]
