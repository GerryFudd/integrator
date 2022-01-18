from general.utils import maximum, vector_sum
from .utils import IterableTable, var_display, resolve_position


class Multipolynomial:
    @staticmethod
    def zero():
        return Multipolynomial([], [])

    @staticmethod
    def one():
        return Multipolynomial([], [1])

    def __init__(self, variables, coefficients):
        self.variables = variables
        self.coefficients = IterableTable(len(variables), coefficients)

    def __get_re_mapper(self, other_variables):
        if len(other_variables) != self.dim:
            return None
        variable_mapping = {}
        remaining = list(range(self.dim))
        for i in range(self.dim):
            to_remove = None
            for j in remaining:
                if self.variables[i] == other_variables[j]:
                    variable_mapping[i] = j
                    to_remove = j
                    break
            if to_remove is not None:
                remaining.remove(to_remove)
        return variable_mapping

    def __eq__(self, other):
        if not isinstance(other, Multipolynomial):
            return False
        # If the parameters are equal, then the instances are
        if self.variables == other.variables and \
                self.coefficients == other.coefficients:
            return True

        # The polynomials are also equal if they use the same variables
        # in a different order
        if self.dim != other.dim:
            return False
        if len(self.coefficients.table) != len(other.coefficients.table):
            return False
        variable_mapping = self.__get_re_mapper(other.variables)
        if len(variable_mapping) < self.dim:
            return False
        for position, value in other.coefficients:
            mapped_position = []
            for x in range(self.dim):
                mapped_position.append(position[variable_mapping[x]])
            if value != self.__get(mapped_position):
                return False
        return True

    def __get(self, position):
        return self.coefficients.get(position)

    def __set(self, position, value):
        return self.coefficients.set(position, value)

    def __has(self, position):
        return self.coefficients.has(position)

    def __next(self, position):
        return self.coefficients.next(position)

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
            if new_term == '':
                new_term = '1'
            result.append(new_term)
        return ' + '.join(result)

    def __repr__(self):
        return f'Multipolynomial(variables={self.variables}, ' \
               f'coefficients={self.coefficients})'

    def __reduce(self):
        variables_to_remove = []
        for i in range(self.dim):
            # variable_index counts backwards intentionally
            # We first reduce the most buried lists in the table (representing
            # the last variable) by removing trailing 0's. Then we walk back
            # to each previous variable and see if it needs to be removed.
            # When a variable is removed, only the ones that follow it are
            # shifted, so we capture the variable indexes in reverse order
            # and remove them that way.
            variable_index = self.dim - i - 1
            max_len = 0
            for position, value in IterableTable(variable_index,
                                                 self.coefficients.table):
                while isinstance(value, list) and len(value) > 0 \
                        and (value[-1] == 0 or value[-1] == []):
                    value.pop()
                max_len = maximum(max_len, len(value))
            if max_len <= 1:
                variables_to_remove.append(variable_index)
        for j in variables_to_remove:
            del self.variables[j]
            self.coefficients.remove_dim(j)
        return self

    def __extend_with(self, other_variables):
        extended_self = self.copy()
        for v in other_variables:
            if not (v in self.variables):
                extended_self.variables.append(v)
                extended_self.coefficients.add_dim()
        return extended_self

    @property
    def dim(self):
        return self.coefficients.dim

    def copy(self):
        return Multipolynomial(
            self.variables.copy(), self.coefficients.table.copy()
        )

    def __do_plus(self, summand):
        result = Multipolynomial(self.variables.copy(), [])
        position = [0] * self.dim
        while self.__has(position) or summand.__has(position):
            a = self.__get(position)
            b = summand.__get(position)
            if a is None:
                result.__set(position, b)
            elif b is None:
                result.__set(position, a)
            else:
                result.__set(position, a + b)
            position = resolve_position(
                self.__next(position),
                summand.__next(position)
            )
        return result.__reduce()

    def plus(self, summand):
        if self.variables != summand.variables:
            if set(self.variables) == set(summand.variables):
                return self.plus(Multipolynomial(
                    self.variables,
                    summand.coefficients.re_map_indices(
                        summand.__get_re_mapper(self.variables)
                    ).table
                ))

            return self.__extend_with(summand.variables)\
                .plus(summand.__extend_with(self.variables))

        return self.__do_plus(summand)

    def times(self, multiplicand):
        result = Multipolynomial(self.variables, [])\
            .__extend_with(multiplicand.variables)

        for pos, val in self.coefficients:
            for other_pos, other_val in multiplicand.coefficients:
                result_pos = vector_sum(pos, other_pos)
                result.__set(
                    result_pos,
                    (result.__get(result_pos) or 0) + val * other_val
                )
        return result.__reduce()

    def power(self, exponent):
        if not isinstance(exponent, int) or exponent < 0:
            raise Exception('Only whole number exponents are supported.')
        if exponent == 0:
            return Multipolynomial.one()
        if exponent == 1:
            return self.copy()

        copies = 1
        result = self.copy()
        while copies < exponent:
            result = result.times(self)
            copies = copies + 1
        return result
