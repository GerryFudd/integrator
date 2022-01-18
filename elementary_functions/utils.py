class TableIterator:
    def __init__(self, coefficients):
        self.position = None
        self.coefficients = coefficients

    def __next__(self):
        self.position = self.coefficients.next(self.position)
        result = self.coefficients.get(self.position)
        if result is None:
            raise StopIteration
        return self.position, result


class IterableTable:
    def __init__(self, dim, table):
        self.dim = dim
        self.table = table

    def __iter__(self):
        return TableIterator(self)

    def __eq__(self, other):
        if not isinstance(other, IterableTable):
            return False
        return self.table == other.table

    def __str__(self):
        return str(self.table)

    def __repr__(self):
        return f'IterableTable(dim={self.dim}, table={self.table})'

    def copy(self):
        return IterableTable(self.dim, self.table.copy())

    def re_map_indices(self, re_mapper):
        new_table = IterableTable(self.dim, [])
        for position, value in self:
            mapped_position = [0] * self.dim
            for i in range(self.dim):
                mapped_position[re_mapper[i]] = position[i]
            new_table.set(mapped_position, value)
        return new_table

    def remove_dim(self, i):
        if i < 0 or self.dim <= i:
            raise IndexError(f'The index {i} is not a removable index for a'
                             f'table with dimension {self.dim}')
        if i == 0:
            if len(self.table) > 1:
                raise Exception(f'The index 0 is not removable because '
                                f'the table {self.table} is not comprised of '
                                f'a single row.')
            elif len(self.table) == 1:
                self.table = self.table[0]
        else:
            for pos, val in IterableTable(i - 1, self.table):
                val_size = len(val)
                for j in range(val_size):
                    if not isinstance(val[j], list):
                        raise Exception(f'The index {i} is not removable because'
                                        f'the value {val} at position {[*pos, j]}'
                                        f'is not a list.')
                    if len(val[j]) > 1:
                        raise Exception(f'The index {i} is not removable '
                                        f'because the value {val[j]} at '
                                        f'position {[*pos, j]} has more than '
                                        f'one element.')
                    elif len(val[j]) == 1:
                        val[j] = val[j][0]
        self.dim = self.dim - 1

    def add_dim(self):
        if self.dim == 0:
            self.table = [0]
        else:
            for position, value in self.copy():
                self.set(position, [value])
        self.dim = self.dim + 1

    def get(self, position):
        if position is None:
            return None
        current = self.table
        for n in position:
            if not isinstance(current, list) or len(current) <= n:
                return None
            current = current[n]
        return current

    def set(self, position, value):
        if len(position) == 0:
            self.table = value
            return
        current = self.table
        for n in position[:-1]:
            while len(current) <= n:
                current.append([])
            current = current[n]
        while len(current) <= position[-1]:
            current.append(0)
        current[position[-1]] = value

    def has(self, position):
        if position is None:
            return False
        current = self.table
        for n in position:
            if not isinstance(current, list) or len(current) <= n:
                return False
            current = current[n]
        return True

    def next(self, position):
        if position is None:
            if self.dim == 0 and len(self.table) == 1:
                return [0]
            return [0] * self.dim
        i = len(position)
        candidate = position.copy()
        while i > 0:
            i = i - 1
            candidate[i] = candidate[i] + 1
            if self.has(candidate):
                return candidate
            candidate[i] = 0
        return None


def var_display(variable, power):
    if power == 0:
        return ''
    if power == 1:
        return variable
    if power >= 10:
        return f'{variable}^({power})'
    return f'{variable}^{power}'


def resolve_position(position_a, position_b):
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
