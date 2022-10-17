from __future__ import annotations

from algebra.linear.equations import MultiDimensionalEquation
from algebra.linear.utils import IndexedMapIterator
from custom_numbers.types import Numeric


class AffineSubspace:
    @staticmethod
    def exact(solution: Point):
        return AffineSubspace(solution)

    @staticmethod
    def pure_subspace(
        linear_subspace: LinearSubspace
    ):
        offset_mapping = {}
        for v in linear_subspace.constrained_variables:
            offset_mapping[v] = 0
        return AffineSubspace(
            Point(offset_mapping, linear_subspace.constrained_variables),
            linear_subspace
        )

    def __init__(
        self,
        offset: Point,
        linear_subspace: LinearSubspace = None,
    ):
        self.offset = offset
        self.linear_subspace = LinearSubspace.trivial(*offset.variable_list) \
            if not linear_subspace else linear_subspace

    @property
    def free_variables(self):
        return self.linear_subspace.free_variables

    @property
    def constrained_variables(self):
        return self.linear_subspace.constrained_variables

    def __str__(self):
        if not self.free_variables:
            return str(self.offset)

        result_lines = []
        for i, out_var, row in self.linear_subspace:
            result_parts = []
            if self.offset[out_var] != 0:
                result_parts.append(str(self.offset[out_var]))
            for j, in_var, c in row:
                result_parts.append(f'{c}{in_var}')

            if not result_parts:
                result_parts.append('0')

            result_line = f'{out_var} = {" + ".join(result_parts)}'
            result_lines.append(result_line)
        return '\n' + '\n'.join(result_lines)

    def to_linear_system(self) -> LinearSystem:
        equations = []
        variables = self.constrained_variables + self.free_variables
        for i, out_var, row in self.linear_subspace:
            equation_mapping = {out_var: 1}
            for j, in_var, c in row:
                equation_mapping[in_var] = -c
            equations.append(MultiDimensionalEquation(
                equation_mapping, self.offset[out_var], variables,
            ))
        return LinearSystem(*equations)

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
                self.to_linear_system().with_vars(variables)
                + other.to_linear_system().with_vars(variables)
            ).solve()
        raise NotImplementedError

    def __repr__(self):
        return f'AffineSubspace(free_variables' \
               f'={self.free_variables},' \
               f'offset={self.offset}, ' \
               f'linear_subspace={self.linear_subspace})'

    def __eq__(self, other):
        return isinstance(other, AffineSubspace) \
            and self.free_variables == other.free_variables \
            and self.constrained_variables == other.constrained_variables \
            and self.offset == other.offset \
            and self.linear_subspace == other.linear_subspace


class LinearSubspace:
    @staticmethod
    def trivial(*variables: str):
        matrix = list(map(lambda _: LinearMapRow.empty(), variables))
        return LinearSubspace(list(variables), [], matrix)

    @staticmethod
    def of(
        constrained_variables: list[str],
        free_variables: list[str],
        matrix: list[list[Numeric]],
    ):
        result_matrix = []
        for list_row in matrix:
            mapping = {}
            for i, c in enumerate(list_row):
                mapping[free_variables[i]] = c
            result_matrix.append(LinearMapRow(
                mapping, free_variables
            ))
        return LinearSubspace(
            constrained_variables, free_variables, result_matrix,
        )

    def __init__(
        self,
        constrained_variables: list[str],
        free_variables: list[str],
        matrix: list[LinearMapRow],
    ):
        self.constrained_variables = constrained_variables
        self.free_variables = free_variables
        self.matrix = matrix

    def __matrix_str(self):
        return '[' + ', '.join(map(str, self.matrix)) + ']'

    def __str__(self):
        return f'{self.__matrix_str()}u -> {self.constrained_variables}'

    def __repr__(self):
        return f'LinearSubspace(variables={self.constrained_variables}, ' \
               f'matrix={self.__matrix_str()})'

    def __eq__(self, other):
        return isinstance(other, LinearSubspace) \
               and self.constrained_variables == other.constrained_variables \
               and self.free_variables == other.free_variables \
               and self.matrix == other.matrix

    def __hash__(self):
        return hash((
            tuple(*self.constrained_variables),
            tuple(*self.free_variables),
            tuple(*self.matrix),
        ))

    def __iter__(self) -> IndexedMapIterator[LinearMapRow]:
        variable_lookup = {}
        for i, v in enumerate(self.constrained_variables):
            variable_lookup[v] = i
        return IndexedMapIterator(
            lambda x: self.matrix[variable_lookup[x]],
            self.constrained_variables,
        )

    def __matmul__(self, other):
        if not isinstance(other, Point):
            return other.__rmatmul__(self)
        result_mapping = {}
        result_variables = self.constrained_variables
        for i, out_var, row in self:
            result_mapping[out_var] = 0
            for j, in_var, c in row:
                result_mapping[out_var] += c * other[in_var]
        return Point(result_mapping, result_variables)


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


class Point:
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
        result_variables = []
        try:
            for i in range(len(self.equations)):
                self.row_echelon_at_index(i)
                result_variables.append(
                    self.variables[self.equations[i].first_non_zero]
                )
            independent_equations = self.equations
        except EndOfEquations as le:
            independent_equations = self.equations[:le.last_index]
        result_subspace = []
        result_offset_mapping = {}
        free_variables = list(filter(
            lambda x: x not in result_variables,
            self.variables
        ))
        for n, eq in enumerate(independent_equations):
            m = eq.first_non_zero
            result_offset_mapping[self.variables[m]] = eq.value / eq[m]
            new_subspace_row = []
            for i, var, c in eq:
                if var in free_variables:
                    new_subspace_row.append(-c)
            result_subspace.append(new_subspace_row)
        result_offset = Point(result_offset_mapping, result_variables)
        return AffineSubspace(
            result_offset,
            LinearSubspace.of(
                result_offset.variable_list,
                free_variables,
                result_subspace,
            )
        )


class InconsistentLinearSystem(Exception):
    pass


class EndOfEquations(Exception):
    def __init__(self, last_index: int):
        self.last_index = last_index
