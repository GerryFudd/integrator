from abc import abstractmethod
from typing import List

from algebra.expression import PolynomialExpression, SolutionType
from algebra.solvable import Solvable, Condition, boundaries_linear, \
    solve_linear_inequality
from general.interval import Interval
from general.numbers import Numeric


class LinearSolvable(Solvable[PolynomialExpression, SolutionType]):
    left: PolynomialExpression
    right: PolynomialExpression
    condition: Condition[SolutionType]

    def boundaries(self) -> List[Numeric]:
        return boundaries_linear(self)

    @abstractmethod
    def solve(self) -> List[SolutionType]:
        """Returns the set where the statement is true"""


class LinearEquation(LinearSolvable[Numeric]):
    def __init__(
        self,
        left: PolynomialExpression,
        right: PolynomialExpression,
    ):
        if len(left) != 2 or len(right) != 2:
            raise NotImplementedError
        self.left = left
        self.right = right
        self.condition = Condition[Numeric](0, True)

    def solve(self) -> List[Numeric]:
        return self.boundaries()


class LinearInequality(LinearSolvable[Interval]):
    def __init__(
        self,
        left: PolynomialExpression,
        right: PolynomialExpression,
        condition: Condition[Interval]
    ):
        if len(left) != 2 or len(right) != 2:
            raise NotImplementedError
        self.left = left
        self.right = right
        self.condition = condition

    def solve(self):
        if self.condition.order == 0:
            raise NotImplementedError
        return solve_linear_inequality(self.boundaries()[0], self.condition)
