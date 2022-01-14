from calculus.utils import maximum


class Polynomial:
    def __init__(self, *coefficients):
        self.coefficients = list(coefficients)

    def __eq__(self, other):
        if not isinstance(other, Polynomial):
            return False
        return self.coefficients == other.coefficients

    def __str__(self):
        result = []
        result.pop()
        for n in range(len(self.coefficients)):
            if self.coefficients[n] == 0:
                pass
            elif n == 0:
                result.append(f'{self.coefficients[0]}')
            elif n == 1:
                result.append(f'{self.coefficients[1]}x')
            elif n >= 10:
                result.append(f'{self.coefficients[n]}x^({n})')
            else:
                result.append(f'{self.coefficients[n]}x^{n}')
        return ' + '.join(result)

    def __repr__(self):
        return f'Polynomial(coefficients={self.coefficients})'

    def __reduce__(self):
        while self.coefficients[-1] == 0:
            self.coefficients.pop()
        return self

    def plus(self, summand):
        coefficients = []
        for n in range(maximum(
            len(self.coefficients), len(summand.coefficients)
        )):
            if n >= len(self.coefficients):
                coefficients.append(summand.coefficients[n])
            elif n >= len(summand.coefficients):
                coefficients.append(self.coefficients[n])
            else:
                coefficients.append(
                    self.coefficients[n] + summand.coefficients[n]
                )
        return Polynomial(*coefficients).__reduce__()

    def times(self, multiplicand):
        self.__reduce__()
        multiplicand.__reduce__()
        coefficients = []
        for n in range(len(self.coefficients)):
            for m in range(len(multiplicand.coefficients)):
                i = n + m
                if i < len(coefficients):
                    coefficients[i] = coefficients[i] \
                                      + self.coefficients[n] \
                                      * multiplicand.coefficients[m]
                else:
                    coefficients.insert(
                        i, self.coefficients[n] * multiplicand.coefficients[m]
                    )
        return Polynomial(*coefficients)


class Multipolynomial:
    def __init__(self, variables, coefficients):
        self.variables = variables
        self.coefficients = coefficients

    def __eq__(self, other):
        if not isinstance(other, Multipolynomial):
            return False
        other_sorted = Multipolynomial(other.variables, other.coefficients) \
            .__sort()
        self_sorted = Multipolynomial(self.variables, self.coefficients) \
            .__sort()
        return self_sorted.variables == other_sorted.variables \
            and self_sorted.coefficients == other_sorted.coefficients

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
        re_mapper = {}
        for i in range(dim):
            for j in range(dim):
                if self.variables[i] == sorted_vars[j]:
                    re_mapper[i] = j
                    break
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
