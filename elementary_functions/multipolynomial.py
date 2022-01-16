from general.utils import maximum
from .utils import IterableTable, var_display, resolve_position


class Multipolynomial:
    def __init__(self, variables, coefficients):
        self.variables = variables
        self.coefficients = IterableTable(len(variables), coefficients)

    def __get_re_mapper(self, other_variables):
        if len(other_variables) != self.coefficients.dim:
            return None
        variable_mapping = {}
        remaining = list(range(self.coefficients.dim))
        for i in range(self.coefficients.dim):
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
        # If the parameters are equal, then the instnaces are
        if self.variables == other.variables and \
                self.coefficients == other.coefficients:
            return True

        # The polynomials are also equal if they use the same variables
        # in a different order
        if self.coefficients.dim != other.coefficients.dim:
            return False
        variable_mapping = self.__get_re_mapper(other.variables)
        if len(variable_mapping) < self.coefficients.dim:
            return False
        for position, value in other.coefficients:
            mapped_position = []
            for x in range(self.coefficients.dim):
                mapped_position.append(position[variable_mapping[x]])
            if value != self.__get(mapped_position):
                return False
        return True

    def __get(self, position):
        return self.coefficients.get(position)

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
            for i in range(self.coefficients.dim):
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
        for i in range(self.coefficients.dim):
            # variable_index counts backwards intentionally
            # We first reduce the most buried lists in the table (representing
            # the last variable) by removing trailing 0's. Then we walk back
            # to each previous variable and see if it needs to be removed.
            # When a variable is removed, only the ones that follow it are
            # shifted, so we capture the variable indexes in reverse order
            # and remove them that way.
            variable_index = self.coefficients.dim - i - 1
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

    def copy(self):
        return Multipolynomial(
            self.variables.copy(), self.coefficients.table.copy()
        )

    def plus(self, summand):
        if self.variables != summand.variables:
            if set(self.variables) == set(summand.variables):
                re_mapper = summand.__get_re_mapper(self.variables)
                re_mapped_coefficients = IterableTable(
                    summand.coefficients.dim,
                    summand.coefficients.table.copy()
                )
                re_mapped_coefficients.re_map_indices(re_mapper)

                return self.plus(Multipolynomial(
                    self.variables,
                    re_mapped_coefficients.table
                ))
            raise Exception('Addition with mismatched variables is not '
                            'supported.')
        coefficients = []
        position = [0] * len(self.variables)
        while self.__has(position) or summand.__has(position):
            current = coefficients
            for i in range(len(self.variables) - 1):
                if position[i] >= len(current):
                    current.insert(position[i], [])
                current = current[position[i]]

            a = self.__get(position)
            b = summand.__get(position)
            if a is None:
                current.append(b)
            elif b is None:
                current.append(a)
            else:
                current.append(a + b)
            position = resolve_position(
                self.__next(position),
                summand.__next(position)
            )
        return Multipolynomial(self.variables, coefficients).__reduce()
