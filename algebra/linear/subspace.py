from __future__ import annotations

from algebra.linear.equations import MultiDimensionalEquation
from algebra.linear.utils import IndexedMapIterator
from custom_numbers.types import Numeric


class AffineSubspace:
    @staticmethod
    def exact(solution: Point):
        variables = solution.variable_list
        equations = []
        for n, v, c in solution:
            equations.append(MultiDimensionalEquation({v: 1}, c, variables))
        return AffineSubspace(LinearSystem(*equations))

    def __init__(
        self,
        linear_system: LinearSystem,
    ):
        self.linear_system = linear_system

    @property
    def offset(self):
        point_builder = Point.builder()
        for _, eq in self.linear_system:
            i = eq.first_non_zero
            if i == len(eq.coefficients):
                continue
            point_builder[eq.variables[i]] = eq[-1] / eq[i]
        return point_builder.build()

    @property
    def free_variables(self):
        result = self.linear_system.variables.copy()
        for v in self.constrained_variables:
            result.remove(v)
        return result

    @property
    def constrained_variables(self):
        return self.offset.variable_list

    def __str__(self):
        result_lines = []
        for i, eq in self.linear_system:
            line_start = None
            result_parts = []
            for j, var, c in eq:
                if c == 0:
                    continue
                if not line_start:
                    line_start = f'{c}{var} = '
                    if eq.value != 0:
                        result_parts.append(str(eq.value))
                else:
                    result_parts.append(f'{-c}{var}')
            if not result_parts:
                result_parts.append('0')
            if not line_start:
                continue
            result_line = f'{line_start}{" + ".join(result_parts)}'
            result_lines.append(result_line)
        return '\n' + '\n'.join(result_lines)

    def to_linear_system(self) -> LinearSystem:
        return self.linear_system

    def __matmul__(self, other):
        if isinstance(other, Point):
            return self @ AffineSubspace.exact(other)
        if isinstance(other, AffineSubspace):
            variables = []
            for v in self.constrained_variables + other.constrained_variables \
                    + other.free_variables + self.free_variables:
                if v not in variables:
                    variables.append(v)
            return (
                self.linear_system.with_vars(variables)
                + other.linear_system.with_vars(variables)
            ).solve()
        raise NotImplementedError

    def __repr__(self):
        return f'AffineSubspace(linear_system={self.linear_system})'

    def __eq__(self, other):
        return isinstance(other, AffineSubspace) \
            and self.linear_system == other.linear_system


class LinearMapRow:
    @staticmethod
    def empty():
        return LinearMapRow({}, [])

    def __str__(self):
        result_parts = []
        for i, var, c in self:
            result_parts.append(f'{c}{var}')
        return '[' + ','.join(result_parts) + ']'

    def __init__(self, mapping: dict[str, Numeric], variables: list[str]):
        self.mapping = mapping
        self.variables = variables

    def __getitem__(self, item):
        if item in self.mapping:
            return self.mapping[item]
        return 0

    def __setitem__(self, key, value):
        self.mapping[key] = value
        if key not in self.variables:
            self.variables.append(key)

    def __iter__(self):
        return IndexedMapIterator(
            lambda x: self[x],
            self.variables,
        )

    def __eq__(self, other):
        return isinstance(other, LinearMapRow) \
            and other.variables == self.variables \
            and other.mapping == self.mapping

    def __hash__(self):
        return hash((self.mapping, *self.variables, 'LinearMapRow'))


class PointBuilder:
    def __init__(self):
        self.mapping = {}
        self.list = []

    def __setitem__(self, key, value):
        self.mapping[key] = value
        if key not in self.list:
            self.list.append(key)

    def map(self, key: str, value: Numeric) -> PointBuilder:
        self[key] = value
        return self

    def build(self):
        return Point(self.mapping, self.list)


class Point:
    @staticmethod
    def builder():
        return PointBuilder()

    def __init__(
        self,
        variable_mapping: dict[str, Numeric],
        variable_list: list[str]
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
            equations.append(MultiDimensionalEquation(
                variable_mapping, value, variables,
            ))
        return LinearSystem(*equations)

    def __init__(self, *equations: MultiDimensionalEquation):
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

    def with_vars(self, variables: list[str]):
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
        return LinearSystem(*new_equations)

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

        self.equations[i] = self.equations[i] / self.equations[i][j]
        for k in range(len(self.equations)):
            if i == k:
                continue
            x = self.equations[k]
            self.equations[k] = x - x[j] * self.equations[i]

    def solve(self) -> AffineSubspace:
        try:
            for i in range(len(self.equations)):
                self.row_echelon_at_index(i)
            independent_equations = self.equations
        except EndOfEquations as le:
            independent_equations = self.equations[:le.last_index]
        return AffineSubspace(LinearSystem(*independent_equations))


class InconsistentLinearSystem(Exception):
    pass


class EndOfEquations(Exception):
    def __init__(self, last_index: int):
        self.last_index = last_index
