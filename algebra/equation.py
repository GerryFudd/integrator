from abc import abstractmethod
from typing import Protocol, runtime_checkable

from general.numbers import Numeric


@runtime_checkable
class Equation(Protocol):
    @abstractmethod
    def solve(self) -> Numeric:
        raise NotImplementedError


class LinearExpression:
    def __init__(self, a: Numeric, b: Numeric):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if isinstance(other, Numeric):
            return self + LinearExpression(0, other)
        if isinstance(other, LinearExpression):
            return LinearExpression(self.a + other.a, self.b + other.b)

    def __mul__(self, other):
        if isinstance(other, Numeric):
            return LinearExpression(self.a * other, self.b * other)
        raise NotImplementedError

    def __truediv__(self, other):
        if isinstance(other, Numeric):
            return LinearExpression(self.a / other, self.b / other)
        raise NotImplementedError


class LinearEquation:
    def __init__(self, left: LinearExpression, right: LinearExpression):
        self.left = left
        self.right = right

    def solve(self) -> Numeric:
        while self.left != LinearExpression(1, 0) or self.right.a != 0:
            if self.left.a == self.right.a == 0:
                raise NotImplementedError
            if self.left.b != 0:
                summand = LinearExpression(-self.right.a, -self.left.b)
                self.left += summand
                self.right += summand
                continue
            if self.left.a != 1:
                divisor = self.left.a
                self.left /= divisor
                self.right /= divisor
                continue
        return self.right.b
