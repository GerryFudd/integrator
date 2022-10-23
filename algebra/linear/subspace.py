from __future__ import annotations

from typing import Generic

from algebra.linear.equations import MultiDimensionalEquation, IndexType
from algebra.linear.utils import IndexedMapIterator, Profiler
from custom_numbers.utils import gcd


class PointBuilder(Generic[IndexType]):
    def __init__(self):
        self.mapping = {}
        self.list: list[IndexType] = []

    def __setitem__(self, key, value):
        self.mapping[key] = value
        if key not in self.list:
            self.list.append(key)

    def map(self, key: IndexType, value: int) -> PointBuilder:
        self[key] = value
        return self

    def build(self):
        return Point[IndexType](self.mapping, self.list)


class Point(Generic[IndexType]):
    @staticmethod
    def builder():
        return PointBuilder()

    def __init__(
        self,
        variable_mapping: dict[IndexType, int],
        variable_list: list[IndexType]
    ):
        self.variable_mapping = variable_mapping
        self.variable_list = variable_list

    def __str__(self):
        return ' + '.join(map(
            lambda x: f'{x[2]}{x[1]}',
            self,
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

    def __iter__(self):
        return IndexedMapIterator(
            lambda v: self[v],
            self.variable_list
        )

    def __add__(self, other):
        if not isinstance(other, Point):
            raise NotImplementedError
        result_mapping = self.variable_mapping.copy()
        for v in other.variable_list:
            if v in self.variable_list:
                result_mapping[v] = self[v] + other[v]
            else:
                result_mapping[v] = other[v]
        return Point(result_mapping, self.variable_list)

    def __hash__(self):
        return hash((self.variable_list, self.variable_mapping))

    def __getitem__(self, item):
        return self.variable_mapping[item] \
            if item in self.variable_mapping \
            else 0


class LinearSystem(Generic[IndexType]):
    @staticmethod
    def of(variables: list[IndexType], table: list[list[int]]) -> LinearSystem[IndexType]:
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
            equations.append(MultiDimensionalEquation[IndexType](
                variable_mapping, value, variables,
            ))
        return LinearSystem(*equations)

    def __init__(self, *equations: MultiDimensionalEquation[IndexType]):
        self.variables = None
        for equation in equations:
            if self.variables is None:
                self.variables = equation.variables
            elif self.variables != equation.variables:
                raise NotImplementedError
        self.equations = list(equations)

    def __str__(self):
        return ' and '.join(map(str, self.equations))

    def __eq__(self, other):
        return isinstance(other, LinearSystem) and set(self.equations) == set(other.equations)

    def with_vars(self, variables: list[IndexType]):
        new_equations = []
        for eq in self.equations:
            new_equation_mapping = {}

            for i, var, c in eq:
                if var not in variables:
                    raise IndexError
                new_equation_mapping[var] = c
            new_equations.append(MultiDimensionalEquation(
                new_equation_mapping, eq.value, variables
            ))
        result = LinearSystem(*new_equations)
        result.sort_rows(0)
        return result

    def merge_mapping(self, mapping: dict[IndexType, int], val):
        new_variables = sorted(mapping.keys())
        for eq in self.equations:
            eq.append_vars(new_variables)
        for v in new_variables:
            if v not in self.variables:
                self.variables.append(v)
        self.equations.append(MultiDimensionalEquation[IndexType](
            mapping, val, self.variables
        ))

    def __iter__(self):
        return enumerate(self.equations).__iter__()

    def __add__(self, other):
        if not isinstance(other, LinearSystem):
            raise NotImplementedError
        variables = self.variables.copy()
        for v in other.variables:
            if v not in variables:
                variables.append(v)
        return LinearSystem(
            *self.with_vars(variables).equations,
            *other.with_vars(variables).equations
        )

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
            raise EndOfEquations(i)

        with Profiler('Zero out equations'):
            for k in range(len(self.equations)):
                if i == k:
                    continue
                if self.equations[k][j] == 0:
                    continue
                x = self.equations[k]
                y = self.equations[i]
                d = gcd(x[j], y[j])
                with Profiler('Recalculate line'):
                    self.equations[k] = (y[j]//d) * x + (-x[j]//d) * y

    def solve(self) -> LinearSystem:
        with Profiler('Row echelon'):
            try:
                for i in range(len(self.equations)):
                    self.row_echelon_at_index(i)
                independent_equations = self.equations
            except EndOfEquations as le:
                independent_equations = self.equations[:le.last_index]
        return LinearSystem(*independent_equations)

    def as_point(self) -> Point | None:
        if len(self.equations) < len(self.variables):
            return None
        result = Point.builder()
        for i, eq in enumerate(self.equations):
            if eq[i] != 1:
                return None
            result.map(self.variables[i], eq.value)
        return result.build()


class InconsistentLinearSystem(Exception):
    pass


class EndOfEquations(Exception):
    def __init__(self, last_index: int):
        self.last_index = last_index
