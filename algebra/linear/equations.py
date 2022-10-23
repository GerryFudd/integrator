from __future__ import annotations
from abc import abstractmethod
from typing import List, TypeVar, Generic

from algebra.expression import PolynomialExpression, SolutionType
from algebra.linear.utils import IndexedMapIterator, Profiler
from algebra.solvable import Solvable, Condition, boundaries_linear, \
    solve_linear_inequality
from custom_numbers.types import Numeric
from general.interval import Interval


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


IndexType = TypeVar('IndexType')


class MultiDimensionalEquation(Generic[IndexType]):
    @staticmethod
    def of_mapping(mapping: dict[IndexType, int], val: int) -> MultiDimensionalEquation[IndexType]:
        return MultiDimensionalEquation(mapping, val, sorted(mapping.keys()))

    def __init__(
        self, variable_mapping: dict[IndexType, int], value: int,
        variables: list[IndexType],
    ):
        self.variables = variables
        self.variable_mapping = variable_mapping
        self.value = value

    def __str__(self):
        terms = []
        for v in self.variables:
            c = self.val(v)
            if c != 0:
                terms.append(f'{c}{v}')
        return f'{" + ".join(terms)} = {self.value}'

    def __iter__(self):
        return IndexedMapIterator(
            lambda v: self.val(v),
            self.variables
        )

    def __getitem__(self, item):
        if item == len(self.variables):
            return self.value
        v = self.variables[item]
        if v in self.variable_mapping:
            return self.variable_mapping[v]
        return 0

    def append_vars(self, variables: list[IndexType]):
        for v in variables:
            if v not in self.variables:
                self.variables.append(v)

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
        if item not in self.variable_mapping:
            return 0
        return self.variable_mapping[item]

    def with_variables(self, variables: list[IndexType]):
        with Profiler('Append variables'):
            result_mapping = {}
            result_variables = variables.copy()
            for v in set(self.variables + variables):
                result_mapping[v] = self.val(v)
                if v not in result_variables:
                    result_variables.append(v)
            return MultiDimensionalEquation(result_mapping, self.value, variables)

    def __add__(self, other):
        with Profiler('Addition'):
            if not isinstance(other, MultiDimensionalEquation) \
                    or self.variables != other.variables:
                raise NotImplementedError
            result_mapping = {}
            for _, v, c in self:
                result_mapping[v] = c + other.val(v)
            return MultiDimensionalEquation(result_mapping, self.value + other.value, self.variables)

    def __sub__(self, other):
        with Profiler('Subtraction'):
            if not isinstance(other, MultiDimensionalEquation) \
                    or self.variables != other.variables:
                raise NotImplementedError
            result_mapping = {}
            for _, v, c in self:
                result_mapping[v] = c - other.val(v)
            return MultiDimensionalEquation(result_mapping, self.value - other.value, self.variables)

    def __rmul__(self, other):
        with Profiler('Scaling'):
            if other == 1:
                return self
            result_mapping = {}
            for _, v, c in self:
                result_mapping[v] = other * c
            return MultiDimensionalEquation(result_mapping, other * self.value, self.variables)

    def __neg__(self):
        with Profiler('Negating'):
            result_mapping = {}
            for _, v, c in self:
                result_mapping[v] = -c
            return MultiDimensionalEquation(result_mapping, -self.value, self.variables)

    @property
    def first_non_zero(self):
        with Profiler('Looking up first non zero'):
            for i, _, c in self:
                if c != 0:
                    return i
            return len(self.variables) if self.value != 0 \
                else len(self.variables) + 1
