from __future__ import annotations
from abc import ABC, abstractmethod
from math import inf
from typing import Generic, List

from algebra.expression import ExpressionType, PolynomialExpression, \
    SolutionType
from elementary_functions.simple import Interval
from custom_numbers.types import Numeric


class Condition(Generic[SolutionType]):
    @staticmethod
    def lt() -> Condition[Interval]:
        return Condition[Interval](-1)

    @staticmethod
    def le() -> Condition[Interval]:
        return Condition[Interval](-1, True)

    @staticmethod
    def gt() -> Condition:
        return Condition[Interval](1)

    @staticmethod
    def ge() -> Condition:
        return Condition[Interval](1, True)

    def __init__(self, order: int, equal: bool = False):
        self.order = order
        self.equal = equal

    def __str__(self):
        result = ''
        if self.order < 0:
            result += '<'
        if self.order > 0:
            result += '>'
        if self.equal:
            result += '='
        return result

    def switch(self):
        return Condition(-self.order, self.equal)


class Solvable(ABC, Generic[ExpressionType, SolutionType]):
    left: ExpressionType
    right: ExpressionType
    condition: Condition[SolutionType]

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
    def boundaries(self) -> List[Numeric]:
        """Returns the list of values where left equals right"""

    @abstractmethod
    def solve(self) -> List[SolutionType]:
        """Returns the set where the statement is true"""


def boundaries_linear(s: Solvable):
    s.add(PolynomialExpression(-s.left[0], -s.right[1]))
    if s.left[1] == 0:
        raise NotImplementedError
    s.scale(1 / s.left[1])
    return [s.right[0]]


def solve_linear_inequality(
    boundary: Numeric, condition: Condition[Interval]
) -> List[Interval]:
    if condition.order < 0:
        return [Interval(
            -inf, boundary,
            include_right=condition.equal
        )]
    return [Interval(
        boundary, inf,
        include_left=condition.equal
    )]
