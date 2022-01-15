class Multipolynomial:
    def __init__(self, variables, coefficients):
        self.variables = variables
        self.coefficients = coefficients

    def __get_re_mapper(self, other_variables):
        dim = len(self.variables)
        if len(other_variables) != dim:
            return None
        variable_mapping = {}
        remaining = list(range(dim))
        for i in range(dim):
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
        dim = len(self.variables)
        if dim != len(other.variables):
            return False
        variable_mapping = self.__get_re_mapper(other.variables)
        position = [0] * dim
        while other.__has(position):
            mapped_position = []
            for x in range(dim):
                mapped_position.append(position[variable_mapping[x]])
            if other.__get(position) != self.__get(mapped_position):
                return False
            position = other.__next(position)
        return True

    def __get(self, position):
        current = self.coefficients
        for i in position:
            if not isinstance(current, list):
                return None
            if i >= len(current):
                return None
            current = current[i]
        return current

    def __has(self, position):
        if position is None:
            return False
        current = self.coefficients
        for i in position:
            if not isinstance(current, list):
                return False
            if i >= len(current):
                return False
            current = current[i]
        return True

    def __next(self, position):
        i = len(position) - 1
        candidate = position.copy()
        while i >= 0:
            candidate[i] = candidate[i] + 1
            if self.__has(candidate):
                return candidate
            candidate[i] = 0
            i = i - 1
        return None

    @staticmethod
    def __var_display(variable, power):
        if power == 0:
            return ''
        if power == 1:
            return variable
        if power >= 10:
            return f'{variable}^({power})'
        return f'{variable}^{power}'

    @staticmethod
    def __resolve_position(position_a, position_b):
        if position_a == position_b:
            return position_a
        if position_a is None:
            return position_b
        if position_b is None:
            return position_a
        if len(position_a) != len(position_b):
            raise Exception('Can\'t compare positions of differing dimension.')

        for i in range(len(position_a)):
            # If one position has a smaller index anywhere starting from the
            # front, then it is earlier
            if position_a[i] < position_b[i]:
                return position_a
            if position_b[i] < position_a[i]:
                return position_b
        raise Exception('Positions should be identical, but didn\'t come out '
                        f'equal\n{position_a}\n{position_b}')

    def __str__(self):
        if len(self.variables) == 0:
            return ''
        result = []
        position = [0] * len(self.variables)

        while position:
            value = self.__get(position)
            if value:
                new_term = ''
                if value == -1:
                    new_term = new_term + '-'
                elif value != 1:
                    new_term = new_term + f'{value}'
                for i in range(len(position)):
                    new_term = new_term + self.__var_display(
                        self.variables[i], position[i]
                    )
                if new_term == '':
                    new_term = '1'
                result.append(new_term)
            position = self.__next(position)
        return ' + '.join(result)

    def __repr__(self):
        return f'Multipolynomial(variables={self.variables}, ' \
               f'coefficients={self.coefficients})'

    def __sort(self):
        dim = len(self.variables)
        sorted_vars = sorted(self.variables)
        re_mapper = self.__get_re_mapper(sorted_vars)
        position = [0] * dim
        re_mapped_coefficients = []
        while self.__has(position):
            target = re_mapped_coefficients
            for k in range(dim - 1):
                re_mapped_pos_k = position[re_mapper[k]]
                while len(target) <= re_mapped_pos_k:
                    target.append([])
                target = target[re_mapped_pos_k]
            target.insert(position[re_mapper[dim - 1]], self.__get(position))
            position = self.__next(position)
        self.variables = sorted_vars
        self.coefficients = re_mapped_coefficients
        return self

    def plus(self, summand):
        if self.variables != summand.variables:
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
            position = self.__resolve_position(
                self.__next(position),
                summand.__next(position)
            )
        return Multipolynomial(self.variables, coefficients)
