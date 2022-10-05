from __future__ import annotations
from abc import ABC, abstractmethod
from math import inf
from typing import Generic, List

from algebra.equation import QuadraticEquation
from algebra.expression import ExpressionType, PolynomialExpression
from elementary_functions.simple import Interval
from general.numbers import Numeric, minimum, maximum


class Condition:
    @staticmethod
    def lt() -> Condition:
        return Condition(True)

    @staticmethod
    def le() -> Condition:
        return Condition(True, True)

    @staticmethod
    def gt() -> Condition:
        return Condition(False)

    @staticmethod
    def ge() -> Condition:
        return Condition(False, True)

    def __init__(self, less_than: bool, equal: bool = False):
        self.less_than = less_than
        self.equal = equal

    def __str__(self):
        result = '<' if self.less_than else '>'
        if self.equal:
            result += '='
        return result

    def switch(self):
        return Condition(not self.less_than, self.equal)


class Inequality(ABC, Generic[ExpressionType]):
    left: ExpressionType
    right: ExpressionType
    condition: Condition

    def __str__(self):
        return f'{self.left} {self.condition} {self.right}'

    def add(self, summand: ExpressionType):
        self.left += summand
        self.right += summand

    def scale(self, scale: Numeric):
        self.left *= scale
        self.right *= scale
        if scale < 0:
            self.condition = self.condition.switch()

    @abstractmethod
    def solve(self) -> List[Interval]:
        """Returns the set where the inequality is true"""


class LinearInequality(Inequality[PolynomialExpression]):
    def __init__(
        self,
        left: PolynomialExpression,
        right: PolynomialExpression,
        condition: Condition,
    ):
        if len(left) != 2 or len(right) != 2:
            raise NotImplementedError
        self.left = left
        self.right = right
        self.condition = condition

    def solve(self) -> List[Interval]:
        self.add(PolynomialExpression(-self.left[0], -self.right[1]))
        if self.left[1] == 0:
            raise NotImplementedError
        if self.left[1] != 1:
            self.scale(1/self.left[1])

        if self.condition.less_than:
            return [Interval(
                -inf, self.right[0],
                include_right=self.condition.equal
            )]
        return [Interval(
            self.right[0], inf,
            include_left=self.condition.equal
        )]


class QuadraticInequality(Inequality[PolynomialExpression]):
    def __init__(
        self, left: PolynomialExpression, right: PolynomialExpression,
        condition: Condition
    ):
        if len(left) != 3 or len(right) != 3:
            raise NotImplementedError
        self.left = left
        self.right = right
        self.condition = condition

    def solve(self) -> List[Interval]:
        boundaries = QuadraticEquation(self.left, self.right).solve()
        if len(boundaries) == 1:
            if (
                self.left[1] > self.right[1] and self.condition.less_than
            ) or (
                self.left[1] < self.right[1] and not self.condition.less_than
            ):
                return [Interval(boundaries[0], inf, self.condition.equal)]
            return [Interval(
                -inf, boundaries[0], include_right=self.condition.equal
            )]
        if (
            self.left[2] > self.right[2] and self.condition.less_than
        ) or (
            self.left[2] < self.right[2] and not self.condition.less_than
        ):
            return [Interval(
                *boundaries,
                self.condition.equal,
                self.condition.equal,
            )]
        return [
            Interval(
                -inf, minimum(*boundaries), include_right=self.condition.equal,
            ),
            Interval(
                maximum(*boundaries), inf, self.condition.equal,
            )
        ]