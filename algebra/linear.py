from abc import abstractmethod
from typing import List

from algebra.expression import PolynomialExpression, SolutionType
from algebra.solvable import Solvable, Condition, boundaries_linear, \
    solve_linear_inequality
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


class Point:
    def __init__(self, variable_mapping: dict[str, Numeric]):
        self.variable_mapping = variable_mapping
        self.variable_list = sorted(self.variable_mapping.keys())

    def __str__(self):
        return ' + '.join(map(
            lambda v: f'{self.variable_mapping[v]}{v}',
            self.variable_list,
        ))

    def __repr__(self):
        assignment_list = ",".join(map(
            lambda v: f'{v}={self.variable_mapping[v]}',
            self.variable_list,
        ))
        return f'Point({assignment_list})'

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.variable_mapping == other.variable_mapping

    def __hash__(self):
        return hash(self.variable_mapping)

    def __getitem__(self, item):
        return self.variable_mapping[item]


class MultiDimensionalEquation(Vector):
    def __init__(self, variable_mapping: dict[str, Numeric], value: Numeric):
        self.variables = sorted(variable_mapping.keys())
        Vector.__init__(self, *map(
            lambda v: variable_mapping[v],
            sorted(self.variables)
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

    @property
    def value(self):
        return self.coefficients[-1]

    def __eq__(self, other):
        if not isinstance(other, MultiDimensionalEquation):
            return False

        return all([
            self.val(v) * other.value == other.val(v) * self.value
            for v in set(self.variables + other.variables)
        ])

    def __hash__(self):
        return hash((
            *self.variables, *self.coefficients, 'MultiDimensionalEquation',
        ))

    def __contains__(self, item):
        return item in self.variables

    def val(self, item):
        return self.coefficients[self.lookup[item]]

    def of_vector(self, base_vector: Vector):
        new_mapping = {}
        for i, val in enumerate(base_vector.coefficients[:-1]):
            new_mapping[self.variables[i]] = val
        return MultiDimensionalEquation(new_mapping, base_vector[-1])

    def __add__(self, other):
        if not isinstance(other, MultiDimensionalEquation) \
                or self.variables != other.variables:
            raise NotImplementedError
        return self.of_vector(Vector.__add__(self, other))

    def __rmul__(self, other):
        return self.of_vector(Vector.__rmul__(self, other))

    @property
    def first_non_zero(self):
        for i, c in enumerate(self.coefficients):
            if c != 0:
                return i

    def test(self, point: Point) -> bool:
        return self.value == sum(map(
            lambda v: self[v] * point[v],
            self.variables
        ))


class AffineSubspace:
    def __init__(
        self, variables: list[str],
        *constraints: MultiDimensionalEquation,
    ):
        self.variables = variables
        self.constraints = list(constraints)

    def __str__(self):
        return ' and '.join(map(str, self.constraints))

    def __repr__(self):
        return f'AffineSubspace({",".join(map(str, self.constraints))})'

    def __eq__(self, other):
        if not isinstance(other, AffineSubspace):
            return False
        return set(self.constraints) == set(other.constraints)

    def contains(self, point: Point):
        return all([c.test(point) for c in self.constraints])


class InconsistentLinearSystem(Exception):
    pass


class EndOfEquations(Exception):
    def __init__(self, last_index: int):
        self.last_index = last_index


class LinearSystem:
    @staticmethod
    def of(variables: list[str], table: list[list[int]]):
        equations = []
        for row in table:
            if len(row) > len(variables) + 1:
                raise IndexError
            variable_mapping = {}
            for i, v in enumerate(variables):
                if len(row) <= i:
                    variable_mapping[v] = 0
                else:
                    variable_mapping[v] = row[i]
            value = 0 if len(row) < len(variables) + 1 else row[len(variables)]
            equations.append(MultiDimensionalEquation(variable_mapping, value))
        return LinearSystem(*equations)

    def __init__(self, *equations: MultiDimensionalEquation):
        self.variables = None
        for equation in equations:
            if self.variables is None:
                self.variables = equation.variables
            elif self.variables != equation.variables:
                raise NotImplementedError
        self.equations = list(equations)

    def sort_rows(self, start_index: int):
        self.equations = self.equations[:start_index] \
            + sorted(
                self.equations[start_index:],
                key=lambda x: x.first_non_zero
            )

    def next_non_zero_from_index(self, i: int):
        if len(self.equations) <= i:
            raise EndOfEquations
        self.sort_rows(i)
        return self.equations[i].first_non_zero

    def row_echelon_at_index(self, i: int):
        j = self.next_non_zero_from_index(i)
        if j == len(self.variables):
            raise InconsistentLinearSystem
        if j > len(self.variables):
            raise EndOfEquations

        self.equations[i] = self.equations[i] / self.equations[i][j]
        for k in range(len(self.variables)):
            if i == k:
                continue
            x = self.equations[k]
            self.equations[k] = x - x[j] * self.equations[i]

    def solve(self) -> AffineSubspace:
        try:
            for i in range(len(self.equations)):
                self.row_echelon_at_index(i)
        except EndOfEquations as le:
            return AffineSubspace(
                self.variables,
                *self.equations[:le.last_index]
            )
        return AffineSubspace(self.variables, *self.equations)
