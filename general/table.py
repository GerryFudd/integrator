from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Callable

from custom_numbers.utils import maximum

DataType = TypeVar('DataType')


class TablePosition:

    @staticmethod
    def with_dim(dim):
        if dim == 0:
            return TablePosition()
        return TablePosition(([0]*(dim-1))+[-1])

    def __init__(
        self, value: list[int] = None, index: int = None
    ):
        self.value = value

    @property
    def dim(self):
        if self.value is None:
            return 0
        return len(self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'TablePosition(value={self.value})'

    def __eq__(self, other):
        if isinstance(other, TablePosition):
            return self.value == other.value
        return False

    def __iter__(self):
        return enumerate(self.value).__iter__()

    def __getitem__(self, item):
        return self.value[item]

    def __len__(self):
        return self.dim

    def __add__(self, other):
        if not isinstance(other, TablePosition):
            raise NotImplementedError
        new_value = []
        new_dim = maximum(self.dim, other.dim)
        for n in range(new_dim):
            if self.dim <= n:
                new_value.append(other[n])
            elif other.dim <= n:
                new_value.append(self[n])
            else:
                new_value.append(self[n] + other[n])
        return TablePosition(new_value)

    @staticmethod
    def __next_value(position: TablePosition, ind: int = -1) -> TablePosition:
        if ind < 0:
            raise StopIteration
        next_value = position.value[:ind]
        next_value.append(position[ind] + 1)
        while len(next_value) < position.dim:
            next_value.append(0)
        return TablePosition(next_value)

    def __next_row(
        self, has_any: Callable[[TablePosition, int], bool]
    ) -> TablePosition:
        ind = self.dim - 1
        next_value = self.__next_value(self, ind)
        has_next = has_any(next_value, ind)
        while ind < self.dim - 1 or not has_next:
            if ind < 0:
                raise StopIteration
            if not has_next:
                ind -= 1
            else:
                next_value = self.__next_value(next_value, ind)
                ind = self.dim - 1
            has_next = has_any(next_value, ind)
        return next_value

    def next(
        self,
        has: Callable[[TablePosition], bool],
        has_any: Callable[[TablePosition, int], bool]
    ) -> TablePosition:
        if self.value is None:
            return TablePosition([0] * self.dim)
        next_value = self.__next_row(has_any)
        while not has(next_value):
            next_value = self.__next_value(next_value)
        return next_value


class DataTable(ABC, Generic[DataType]):
    @staticmethod
    @abstractmethod
    def of(dim: int, values: list | DataType, zero: DataType):
        """Construct a table from a dimension and values"""

    dim: int
    values: list | DataType
    zero: DataType

    def copy(self):
        return self.of(self.dim, self.values.copy(), self.zero)

    def __str__(self):
        return str(self.values)

    def __repr__(self):
        return f'DataTable(dim={self.dim}, values={self.values})'

    def __eq__(self, other):
        if not isinstance(other, DataTable):
            return False
        return self.dim == other.dim and self.values == other.values

    def __hash__(self):
        return hash((self.values, 'DataTable'))

    def has(self, position: TablePosition) -> bool:
        current = self.values
        for _, index in position:
            if not isinstance(current, list) or len(current) <= index:
                return False
            current = current[index]
        return True

    def has_any(self, position: TablePosition, i: int) -> bool:
        current = self.values
        for dim, index in position:
            if not isinstance(current, list) or len(current) <= index:
                return False
            if dim == i \
                    and isinstance(current, list) \
                    and len(current) > index:
                for item in current[index:]:
                    if not isinstance(item, list) or len(item) > 0:
                        return True
                return False
            current = current[index]
        return True

    def __getitem__(self, item):
        if not isinstance(item, TablePosition):
            raise NotImplementedError
        if item.value is None:
            return None
        current: list | DataType = self.values
        for dim, index in item:
            if dim >= self.dim or not isinstance(current, list):
                raise IndexError
            if len(current) <= index:
                return 0
            current = current[index]
        return current

    def __setitem__(self, key, value):
        if not isinstance(key, TablePosition):
            raise NotImplementedError
        current: list | DataType = self.values
        if self.dim == key.dim == 0:
            self.values = value
        for dim, index in key:
            if dim == self.dim - 1:
                while len(current) <= index:
                    if value == self.zero:
                        return
                    current.append(self.zero)
                current[index] = value
                return
            if dim >= self.dim:
                raise IndexError
            while len(current) <= index:
                if value == self.zero:
                    return
                current.append([])
            current = current[index]


class TableIterator(Generic[DataType]):
    def __init__(self, table: DataTable[DataType]):
        self.position = TablePosition.with_dim(table.dim)

        self.table = table

    def __str__(self):
        return f'{self.table}@{self.position}'

    def __repr__(self):
        return f'TableIterator(position={self.position},table={self.table})'

    def __next__(self) -> tuple[TablePosition, DataType]:
        self.position = self.position.next(self.table.has, self.table.has_any)

        return self.position, self.table[self.position]


class AnyTableIterator(Generic[DataType]):
    def __init__(self, tables: list[DataTable[DataType]]):
        self.position = TablePosition.with_dim(
            max(map(lambda x: x.dim, tables))
        )
        self.tables = tables

    def __str__(self):
        return f'{",".join(map(str,self.tables))}@{self.position}'

    def __repr__(self):
        return f'TableIterator(position={self.position},' \
               f'{",".join(map(str,self.tables))})'

    def __has(self, position: TablePosition) -> bool:
        for table in self.tables:
            if table.has(position):
                return True
        return False

    def __has_any(self, position: TablePosition, i: int) -> bool:
        for table in self.tables:
            if table.has_any(position, i):
                return True
        return False

    def __next__(self) -> tuple[TablePosition, list[DataType]]:
        self.position = self.position.next(self.__has, self.__has_any)

        result = []
        for t in self.tables:
            if t.has(self.position):
                result.append(t[self.position])
            else:
                result.append(t.zero)

        return self.position, result


class AnyTableIterable(Generic[DataType]):
    def __init__(self, *tables: DataTable[DataType]):
        self.tables = list(tables)

    def __iter__(self):
        return AnyTableIterator(self.tables)


class IterableTable(DataTable[DataType], Generic[DataType]):
    @staticmethod
    def of(dim: int, values: list, zero: DataType):
        return IterableTable(dim, values, zero)

    def __init__(self, dim: int, values: list[list | DataType], zero: DataType):
        self.dim = dim
        self.values = values
        self.zero = zero

    def __iter__(self) -> TableIterator[DataType]:
        return TableIterator(self)


def remove_dim(table: DataTable[DataType], i: int) -> DataTable[DataType]:
    if table.dim <= 0 or table.dim <= i:
        raise IndexError
    if table.dim == 1:
        if len(table.values) > 1:
            raise IndexError
        return table.of(
            0,
            table.values[0] if len(table.values) == 1 else table.zero,
            table.zero
        )
    new_table = table.of(table.dim - 1, [], table.zero)
    for position, value in table:
        if position[i] != 0:
            if value != 0:
                raise IndexError(f'The dimension {i} is not removable because'
                                 f' there is a non-zero value {value} at position'
                                 f' {position}')
        else:
            new_position = TablePosition(
                position.value[:i] + position.value[i+1:]
            )
            new_table[new_position] = value
    return new_table


def add_dim(table: DataTable[DataType]) -> DataTable[DataType]:
    if table.dim == 0:
        return table.of(1, [table.values], table.zero)
    new_table = table.of(table.dim, [], [table.zero])
    for position, value in IterableTable(table.dim, table.values, table.zero):
        new_table[position] = [value]
    return table.of(table.dim + 1, new_table.values, table.zero)
