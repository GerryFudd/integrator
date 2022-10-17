from abc import abstractmethod
from typing import List

from algebra.expression import PolynomialExpression, SolutionType
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

    def __iter__(self):
        return enumerate(map(
            lambda v: self.variable_mapping[v],
            self.variable_list
        )).__iter__()

    def __add__(self, other):
        if not isinstance(other, Point):
            raise NotImplementedError
        result_mapping = self.variable_mapping.copy()
        for v in other.variable_list:
            if v in self.variable_list:
                result_mapping[v] = self[v] + other[v]
            else:
                result_mapping[v] = other[v]
        return Point(result_mapping)

    def __hash__(self):
        return hash(self.variable_mapping)

    def __contains__(self, item):
        return item in self.variable_mapping

    def __getitem__(self, item):
        return self.variable_mapping[item]


class MultiDimensionalEquation(Vector):
    def __init__(self, variable_mapping: dict[str, Numeric], value: Numeric):
        self.variables = sorted(variable_mapping.keys())
        Vector.__init__(self, *map(
            lambda v: RationalNumber.of(variable_mapping[v]),
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
            *self.variables,
            *map(lambda x: x / self.value, self.coefficients),
            'MultiDimensionalEquation',
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

    def __truediv__(self, other):
        return self.of_vector(Vector.__rmul__(
            self, RationalNumber.of(other).flip()
        ))

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


class LinearSubspace:
    @staticmethod
    def trivial(*variables: str):
        return LinearSubspace(list(variables), [[]] * len(variables))

    def __init__(self, variables: list[str], matrix: list[list[Numeric]]):
        self.variables = variables
        self.matrix = matrix

    def __str__(self):
        return f'{self.matrix}u -> {self.variables}'

    def __repr__(self):
        return f'LinearSubspace(variables={self.variables}, ' \
               f'matrix={self.matrix})'

    def __eq__(self, other):
        return isinstance(other, LinearSubspace) \
            and self.variables == other.variables \
            and self.matrix == other.matrix

    def __hash__(self):
        matrix_snapshot = tuple(*map(lambda x: tuple(*x), self.matrix))
        return hash((tuple(*self.variables), matrix_snapshot))

    def __matmul__(self, other):
        if not isinstance(other, Point):
            raise NotImplementedError
        result_mapping = {}
        for i, var in enumerate(self.variables):
            if var in other.variable_list:
                raise IndexError
            result_mapping[var] = sum(map(
                lambda x: self.matrix[i][x[0]] * x[1],
                other
            ))
        return Point(result_mapping)


class AffineSubspace:
    @staticmethod
    def exact(solution: Point):
        return AffineSubspace(solution.variable_list, solution)

    @staticmethod
    def pure_subspace(
        other_variables: list[str],
        linear_subspace: LinearSubspace
    ):
        offset_mapping = {}
        for v in linear_subspace.variables:
            offset_mapping[v] = 0
        return AffineSubspace(
            linear_subspace.variables + other_variables,
            Point(offset_mapping),
            linear_subspace
        )

    def __init__(
        self, variables: list[str],
        offset: Point,
        linear_subspace: LinearSubspace = None,
    ):
        self.variables = variables
        self.offset = offset
        self.linear_subspace = LinearSubspace.trivial(*offset.variable_list) \
            if not linear_subspace else linear_subspace

    @property
    def free_variables(self):
        return list(filter(
            lambda x: x not in self.linear_subspace.variables,
            self.variables
        ))

    @property
    def constrained_variables(self):
        return self.linear_subspace.variables

    def __str__(self):
        if not self.linear_subspace.variables:
            return str(self.offset)

        result_lines = []
        while len(result_lines) < max(len(self.free_variables),
                                      len(self.linear_subspace.variables)):
            new_line = ''
            if len(result_lines) == 0:
                new_line += f'{self.offset} + '
            if len(result_lines) < len(self.linear_subspace.variables):
                matrix_row = " ".join(map(
                    str, self.linear_subspace.variables[len(result_lines)]
                ))
                new_line += f'|{matrix_row}|'
                if len(result_lines) < len(self.free_variables):
                    new_line += f'|{self.free_variables[len(new_line)]}|'
            elif len(result_lines) < len(self.free_variables):
                new_line += ' ' * (2 * len(self.free_variables) + 1)
                new_line += f'|{self.free_variables[len(new_line)]}|'
            result_lines.append(new_line)

    def __repr__(self):
        return f'AffineSubspace(free_variables={self.free_variables},' \
               f'offset={self.offset}, ' \
               f'linear_subspace={self.linear_subspace})'

    def __eq__(self, other):
        return isinstance(other, AffineSubspace) \
            and self.free_variables == other.free_variables \
            and self.offset == other.offset \
            and self.linear_subspace == other.linear_subspace

    def contains(self, point: Point):
        free_part = {}
        constrained_part = point.variable_mapping.copy()
        for v in self.free_variables:
            if v not in point:
                return False
            free_part[v] = point[v]
            del constrained_part[v]

        return Point(free_part) == self.offset \
            + (self.linear_subspace @ Point(constrained_part))


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
        result_offset_mapping = {}
        result_subspace = []
        for n, eq in enumerate(independent_equations):
            result_offset_mapping[self.variables[n]] = eq.value / eq[n]
            result_subspace.append(list(map(
                lambda x: -x, eq.coefficients[len(independent_equations):-1]
            )))
        result_offset = Point(result_offset_mapping)
        return AffineSubspace(
            self.variables,
            Point(result_offset_mapping),
            LinearSubspace(result_offset.variable_list, result_subspace)
        )
