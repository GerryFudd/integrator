from abc import abstractmethod
from math import inf
from typing import List

from algebra.expression import PolynomialExpression, SolutionType
from algebra.solvable import Solvable, boundaries_linear, Condition, \
    solve_linear_inequality
from general.interval import Interval
from custom_numbers.computation import Number
from custom_numbers.types import Numeric
from custom_numbers.utils import minimum, maximum


class QuadraticSolvable(Solvable[PolynomialExpression, SolutionType]):
    @property
    def is_linear(self) -> bool:
        return self.left[2] == self.right[2]

    def boundaries(self) -> List[Numeric]:
        if self.is_linear:
            return boundaries_linear(self)
        self.add(-self.right)
        self.scale(1 / self.left[2])

        u = Number.of(self.left[1]) / 2
        v = (u ** 2 - self.left[0]) ** 0.5
        return [-u - v, -u + v]

    @abstractmethod
    def solve(self) -> List[SolutionType]:
        """Returns the set where the statement is true"""


class QuadraticEquation(QuadraticSolvable[Numeric]):
    def __init__(
        self, left: PolynomialExpression, right: PolynomialExpression
    ):
        if len(left) != 3 or len(right) != 3:
            raise NotImplementedError
        self.left = left
        self.right = right
        self.condition = Condition[Numeric](0, True)

    def solve(self) -> List[Numeric]:
        return self.boundaries()


class QuadraticInequality(QuadraticSolvable[Interval]):
    def __init__(
        self, left: PolynomialExpression, right: PolynomialExpression,
        condition: Condition[SolutionType]
    ):
        if len(left) != 3 or len(right) != 3:
            raise NotImplementedError
        self.left = left
        self.right = right
        self.condition = condition

    def solve(self) -> List[Interval]:
        boundaries = self.boundaries()
        if self.is_linear:
            return solve_linear_inequality(boundaries[0], self.condition)
        if self.condition.order < 0:
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
