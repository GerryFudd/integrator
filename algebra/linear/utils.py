from __future__ import annotations

from typing import Generic, Callable, TypeVar

from custom_numbers.types import Numeric

IterationValType = TypeVar('IterationValType')


class IndexedMapIterator(Generic[IterationValType]):
    def __init__(
        self, mapping: Callable[[str], IterationValType], key_index: list[str],
    ):
        self.mapping = mapping
        self.key_index = key_index
        self.current = -1

    def __next__(self) -> tuple[int, str, Numeric]:
        self.current += 1
        if self.current >= len(self.key_index):
            raise StopIteration
        key = self.key_index[self.current]
        return self.current, key, self.mapping(key)
