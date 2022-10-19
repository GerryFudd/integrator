from __future__ import annotations
from abc import abstractmethod
from typing import List

from algebra.expression import PolynomialExpression, SolutionType
from algebra.linear.utils import IndexedMapIterator
from algebra.solvable import Solvable, Condition, boundaries_linear, \
    solve_linear_inequality
from custom_numbers.exact.rational_number import RationalNumber
from custom_numbers.types import Numeric
from general.interval import Interval
from general.vector import Vector


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


class MultiDimensionalEquation(Vector):
    def __init__(
        self, variable_mapping: dict[str, Numeric], value: Numeric,
        variables: list[str],
    ):
        self.variables = variables
        Vector.__init__(self, *map(
            lambda v: RationalNumber.of(variable_mapping[v])
            if v in variable_mapping
            else RationalNumber.of(0),
            self.variables
        ), value)
        self.lookup = {}
        for i, val in enumerate(self.variables):
            self.lookup[val] = i

    def __str__(self):
        terms = []
        for v in self.variables:
            c = self.val(v)
            if c != 0:
                terms.append(f'{c}{v}')
        return f'{" + ".join(terms)} = {self.value}'

    def __iter__(self):
        return IndexedMapIterator(
            lambda v: self.coefficients[self.lookup[v]]
            if v in self.lookup
            else 0,
            self.variables
        )

    @property
    def value(self):
        return self.coefficients[-1]

    @property
    def non_zero_count(self):
        return len(list(filter(lambda x: x != 0, self.coefficients[:-1])))

    def __normalized_coefficients(self):
        divisor = 0
        sorted_vars = sorted(self.variables)
        for v in sorted_vars:
            divisor = self.val(v)
            if divisor != 0:
                return list(filter(
                    lambda x: x[1] != 0,
                    map(lambda x: (x, self.val(x) / divisor), sorted_vars)),
                ) + [(None, self.value / divisor)]

        return []

    def __eq__(self, other):
        if not isinstance(other, MultiDimensionalEquation):
            return False

        return self.__normalized_coefficients() == other.__normalized_coefficients()

    def __hash__(self):
        return hash((
            *self.__normalized_coefficients(),
            'MultiDimensionalEquation',
        ))

    def __contains__(self, item):
        return item in self.variables

    def val(self, item):
        if item not in self.lookup:
            return RationalNumber()
        return self.coefficients[self.lookup[item]]

    def of_vector(self, base_vector: Vector):
        new_mapping = {}
        for i, val in enumerate(base_vector.coefficients[:-1]):
            new_mapping[self.variables[i]] = val
        return MultiDimensionalEquation(
            new_mapping, base_vector[-1], self.variables
        )

    def with_variables(self, variables: list[str]):
        result_mapping = {}
        result_variables = variables.copy()
        for v in set(self.variables + variables):
            result_mapping[v] = self.val(v)
            if v not in result_variables:
                result_variables.append(v)
        return MultiDimensionalEquation(result_mapping, self.value, variables)

    def __add__(self, other):
        if not isinstance(other, MultiDimensionalEquation) \
                or self.variables != other.variables:
            raise NotImplementedError
        return self.of_vector(Vector.__add__(self, other))

    def __rmul__(self, other):
        return self.of_vector(Vector.__rmul__(self, other))

    def __truediv__(self, other):
        return self.of_vector(Vector.__rmul__(
            self, RationalNumber.of(other).flip()
        ))

    @property
    def first_non_zero(self):
        for i, _, c in self:
            if c != 0:
                return i
        return len(self.variables) if self.value != 0 \
            else len(self.variables) + 1
