from __future__ import annotations

from typing import Generic

from algebra.linear.equations import MultiDimensionalEquation, IndexType
from algebra.linear.utils import Profiler
from custom_numbers.exact.rational_number import RationalNumber
from custom_numbers.utils import gcd


class KnownValue(Generic[IndexType]):
    def __init__(self, variable: IndexType, equals_value: int, coefficient: int = 1):
        self.coefficient = coefficient
        self.equals_value = equals_value
        self.variable = variable

    def __str__(self):
        return f'{self.coefficient}{self.variable}={self.equals_value}'

    def __repr__(self):
        return f'KnownValue(variable={self.variable},equals_value={self.equals_value},coefficient={self.coefficient})'

    def __eq__(self, other):
        return isinstance(other, KnownValue) and self.variable == other.variable \
               and self.equals_value * other.coefficient == other.equals_value * self.coefficient

    def __hash__(self):
        d = gcd(self.equals_value, self.coefficient)

        return hash((self.equals_value//d, self.coefficient//d, self.variable, 'KnownValue'))

    def reduced(self) -> tuple[int, int]:
        if self.coefficient == 1:
            return self.equals_value, self.coefficient
        d = gcd(self.equals_value, self.coefficient)
        return self.equals_value//d, self.coefficient//d

    @property
    def value(self):
        if self.coefficient == 1:
            return self.equals_value
        a, b = divmod(self.equals_value, self.coefficient)
        if b == 0:
            self.coefficient = 1
            self.equals_value = a
            return a
        return RationalNumber(self.equals_value, self.coefficient)


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

    def known_values(self) -> dict[IndexType, KnownValue[IndexType]]:
        result = {}
        for _, eq in self:
            candidate = None
            for v, c in eq.variable_mapping.items():
                if c == 0:
                    continue
                if candidate is not None:
                    candidate = None
                    break
                else:
                    candidate = KnownValue(v, eq.value, c)
            if candidate is not None:
                result[candidate.variable] = candidate
        return result


class InconsistentLinearSystem(Exception):
    pass


class EndOfEquations(Exception):
    def __init__(self, last_index: int):
        self.last_index = last_index
