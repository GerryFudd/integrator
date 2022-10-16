from __future__ import annotations

from typing import Callable

from general.table import IterableTable, TablePosition, remove_dim, AnyTableIterable


def var_display(variable, power):
    if power == 0:
        return ''
    if power == 1:
        return variable
    if power >= 10:
        return f'{variable}^({power})'
    return f'{variable}^{power}'


class ReMapper:
    def __init__(self, index_mapping: list[int]):
        self.index_mapping = index_mapping

    def remap(self, position: TablePosition):
        return TablePosition(
            [position.value[n] for n in self.index_mapping]
        )


class Multipolynomial:

    @staticmethod
    def named(param):
        return Multipolynomial([param], [0, 1])

    @staticmethod
    def zero():
        return Multipolynomial([], 0)

    @staticmethod
    def one():
        return Multipolynomial([], 1)

    def __init__(self, variables, coefficients=None):
        self.variables = variables
        if coefficients is None:
            coefficients = 0 if len(self.variables) == 0 else []
        self.coefficients = IterableTable(len(variables), coefficients, 0)

    # re_mapper = self.variables^-1 o other.variables
    def get_re_mapper(self, other_variables: list[str]) -> ReMapper:
        if len(other_variables) != self.dim:
            raise IndexError

        self_variables_inverse = {}
        for self_dim, val in enumerate(self.variables):
            self_variables_inverse[val] = self_dim
        return ReMapper(list(map(
            lambda x: self_variables_inverse[x], other_variables
        )))

    def re_map_indices(self) -> Multipolynomial:
        if self.dim == 0 or self.dim == 1:
            return self

        other_variables: list[str] = sorted(self.variables)
        if other_variables == self.variables:
            return self

        re_mapper = self.get_re_mapper(other_variables)

        result_indices = IterableTable(self.dim, [], 0)
        # position p[0],...,p[dim-1] points to the coefficient of
        # self.variables[0]^p[0]...self.variables[dim-1]^p[dim-1]
        for position, value in self.coefficients:
            # Suppose a, b, and c are distinct indices between 0 and dim-1 and
            # self.values[a]='x', self.values[b]='y', and self.values[c]='z'.
            # If p[a]=i, p[b]=j, and p[c]=k with p[n]=0 for all other
            # indices, then self[p] = v implies that x^iy^jz^k has coefficient
            # v.
            #
            # Now suppose that other.values[a]='y', other.values[b]='z',
            # and other.values[c]='x'. To indicate that the coefficient of
            # x^iy^jz^k is v we must assign other[q]=v where q[c]=i,
            # q[a]=j, and q[b]=k with all other q[n]=0.
            # in this case
            # re_mapper[a]=self.values^-1('y')=b
            # re_mapper[b]=self.values^-1('z')=c
            # re_mapper[c]=self.values^-1('x')=a
            # and q[n]:=p[re_mapper[n]] results in
            # q[a]=p[re_mapper[a]]=p[b]=j
            # q[b]=p[re_mapper[b]]=p[c]=k
            # q[c]=p[re_mapper[c]]=p[a]=i
            #
            # self.variables(self.variables^-1(
            #   other.variables[m]
            # ))^q[m]=self.variables(
            #   self.variables^-1(other.variables[n])
            # )^p[self.variables^-1(other.variables[n])]
            # implying q[m] = p[self.variables^-1(other.variables(m))

            # Therefore q[other.variables^-1(self.variables(n))]=p[n]
            result_indices[re_mapper.remap(position)] = value
        return Multipolynomial(other_variables, result_indices.values)

    def __eq__(self, other):
        if not isinstance(other, Multipolynomial):
            return False
        return self.variables == other.variables \
            and self.coefficients.values == other.coefficients.values

    def __getitem__(self, position):
        val = self.coefficients[position]
        return 0 if val is None else val

    def __setitem__(self, position, value):
        self.coefficients[position] = value

    def __str__(self):
        if len(self.variables) == 0:
            return ''
        result = []

        for position, value in self.coefficients:
            if value == 0:
                continue
            new_term = ''
            if value == -1:
                new_term = new_term + '-'
            elif value != 1:
                new_term = new_term + f'{value}'
            for i in range(self.dim):
                new_term = new_term + var_display(
                    self.variables[i], position[i]
                )
            if new_term in ('', '-'):
                new_term += '1'
            result.append(new_term)
        return ' + '.join(result)

    def __repr__(self):
        return f'Multipolynomial(variables={self.variables}, ' \
               f'coefficients={self.coefficients})'

    def __trim_trailing_zeros(self):
        codimension_zero = 0
        for i in range(self.dim):
            codimension_zero = [codimension_zero]
            current_dim = self.dim - i - 1
            for position, value in IterableTable(
                current_dim, self.coefficients.values,
                codimension_zero
            ):
                if isinstance(value, list):
                    while True:
                        if len(value) == 0:
                            break
                        elif isinstance(value[-1], list) \
                                and len(value[-1]) == 0:
                            value.pop()
                        elif value[-1] == 0:
                            value.pop()
                        else:
                            break

    def _reduce(self):
        result = self.copy()
        if self.dim == 0:
            return result
        variables_to_keep = set()

        for position, value in self.coefficients:
            if value != 0:
                for dim, index in position:
                    if index > 0:
                        variables_to_keep.add(dim)
                if len(variables_to_keep) == self.dim:
                    break

        for j in sorted(list(range(self.dim)), reverse=True):
            if j not in variables_to_keep:
                del result.variables[j]
                result.coefficients = remove_dim(result.coefficients, j)
        self.__trim_trailing_zeros()
        return result

    def extend_with(self, other_variables):
        new_variables = []
        for v in other_variables:
            if v not in self.variables:
                new_variables.append(v)
        result = Multipolynomial(self.variables.copy() + new_variables)
        for position, value in self.coefficients:
            new_position = TablePosition(
                position.value + ([0]*(result.dim - self.dim))
            )
            result[new_position] = value
        return result

    @property
    def dim(self):
        return self.coefficients.dim

    def copy(self):
        return Multipolynomial(
            self.variables.copy(),
            self.coefficients.values
            if self.coefficients.dim == 0
            else self.coefficients.values.copy()
        )

    def __unify_variables_and_do(
        self, other: Multipolynomial,
        action: Callable[[Multipolynomial, Multipolynomial], Multipolynomial],
    ) -> Multipolynomial:

        x = self.extend_with(other.variables).re_map_indices()
        y = other.extend_with(x.variables).re_map_indices()

        result = action(x, y)
        return result

    def __do_add(self, summand):
        result = Multipolynomial(self.variables.copy(), [])
        for position, values in AnyTableIterable(
            self.coefficients, summand.coefficients
        ):
            result[position] = sum(values)
        return result._reduce()

    def __add__(self, other):
        if isinstance(other, int):
            return self + Multipolynomial([], other)
        if not isinstance(other, Multipolynomial):
            raise NotImplementedError
        result = self.__unify_variables_and_do(
            other, lambda x, y: x.__do_add(y)
        )
        return result

    def __sub__(self, other):
        return self + -other

    def __neg__(self):
        result = Multipolynomial(self.variables)
        for pos, val in self.coefficients:
            result[pos] = -val
        return result

    def __do_mul(self, multiplicand: Multipolynomial):
        result = Multipolynomial(self.variables.copy())

        for pos, val in self.coefficients:
            for other_pos, other_val in multiplicand.coefficients:
                result_pos = pos + other_pos
                result[result_pos] = (result[result_pos] or 0) + val * other_val
        return result._reduce()

    def __mul__(self, other):
        if not isinstance(other, Multipolynomial):
            raise NotImplementedError

        return self.__unify_variables_and_do(
            other, lambda x, y: x.__do_mul(y)
        )

    def __rmul__(self, other):
        if isinstance(other, int):
            return Multipolynomial([], other) * self
        return self * other

    def __pow__(self, power, modulo=None):
        if not isinstance(power, int) or power < 0:
            raise NotImplementedError
        copies = 0
        result = Multipolynomial.one()
        while copies < power:
            result *= self
            copies += 1
        return result
