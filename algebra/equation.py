from abc import abstractmethod, ABC
from typing import List, Callable, Generic

from algebra.expression import PolynomialExpression, ExpressionType
from general.numbers import Numeric, RationalNumber


class Equation(ABC, Generic[ExpressionType]):
    left: ExpressionType
    right: ExpressionType

    def __str__(self):
        return f'{self.left} = {self.right}'

    def modify_both(self, do_mod: Callable[[ExpressionType], ExpressionType]):
        self.left = do_mod(self.left)
        self.right = do_mod(self.right)

    def add(self, summand: ExpressionType):
        self.modify_both(lambda x: x + summand)

    def scale(self, scale: Numeric):
        self.modify_both(lambda x: scale * x)

    @abstractmethod
    def solve(self) -> List[Numeric]:
        pass


class LinearEquation(Equation[PolynomialExpression]):
    def __init__(self, left: PolynomialExpression, right: PolynomialExpression):
        if len(left) != 2 or len(right) != 2:
            raise NotImplementedError
        self.left = left
        self.right = right

    def solve(self) -> List[Numeric]:
        while self.left != PolynomialExpression(0, 1) or self.right[1] != 0:
            if self.left[1] == self.right[1] == 0:
                raise NotImplementedError
            if self.left[0] != 0:
                self.add(PolynomialExpression(-self.left[0], -self.right[1]))
                continue
            if self.left[1] != 1:
                self.scale(1/self.left[1])
                continue
        return [self.right[0]]


class QuadraticEquation(Equation[PolynomialExpression]):
    def __init__(self, left: PolynomialExpression, right: PolynomialExpression):
        if len(left) != 3 or len(right) != 3:
            raise NotImplementedError
        self.left = left
        self.right = right

    def solve(self) -> List[Numeric]:
        if self.right != PolynomialExpression(0, 0, 0):
            self.add(-self.right)
        if self.left[1] == self.left[2] == 0:
            raise NotImplementedError
        if self.left[2] == 0:
            return LinearEquation(
                PolynomialExpression(*self.left[:2]),
                PolynomialExpression(*self.right[:2])
            ).solve()

        u = RationalNumber.resolve(self.left[1])/(2 * self.left[2])
        v = (u ** 2 - self.left[0]) ** 0.5
        return [-u - v, -u + v]
