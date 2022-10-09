from __future__ import annotations

from math import inf
from typing import List

from elementary_functions.utils import FunctionSum, ConstantFunction
from general.interval import Interval
from custom_numbers.types import Numeric


class CharacteristicFunction:
    def __init__(self, domain: Interval, coefficient: Numeric = 1):
        self.domain = domain
        self.coefficient = coefficient

    def __str__(self):
        return f'{self.coefficient}X_{self.domain}'

    def __repr__(self):
        return f'CharacteristicFunction(domain={self.domain},coefficient=' \
               f'{self.coefficient})'

    def __eq__(self, other):
        if isinstance(other, ConstantFunction) \
                and self.domain == Interval(-inf, inf):
            return self.coefficient == other.val
        return isinstance(other, CharacteristicFunction) \
            and self.domain == other.domain

    def __hash__(self):
        return hash((self.domain, self.coefficient, 'CharacteristicFunction'))

    def evaluate(self, x: Numeric) -> Numeric:
        if self.domain.contains(x):
            return self.coefficient
        return 0

    def __mul__(self, other):
        raise NotImplementedError

    def __rmul__(self, other):
        return CharacteristicFunction(self.domain, other * self.coefficient)

    def __add__(self, other):
        if isinstance(other, CharacteristicFunction):
            if self.domain.intersects(other.domain):
                characteristic_functions = [CharacteristicFunction(
                    self.domain * other.domain,
                    self.coefficient + other.coefficient
                )]
                for remainder in self.domain - other.domain:
                    characteristic_functions.append(CharacteristicFunction(
                        remainder, self.coefficient
                    ))
                return SimpleFunction(*characteristic_functions)

            return SimpleFunction(self, other)
        if isinstance(other, SimpleFunction):
            return other + self
        return FunctionSum(self, other)

    def __matmul__(self, other):
        raise NotImplementedError


class SimpleFunction:
    def __init__(self, *linear_combo: CharacteristicFunction):
        self.constituents: List[CharacteristicFunction] = list(linear_combo)

    def __str__(self):
        return ' + '.join(map(
            str,
            filter(lambda x: x.coefficient != 0, self.constituents)
        ))

    def __repr__(self):
        return f'SimpleFunction({",".join(map(str, self.constituents))})'

    def __eq__(self, other):
        if isinstance(other, CharacteristicFunction):
            return len(self.constituents) == 1 and self.constituents[0] == other
        return isinstance(other, SimpleFunction) \
            and set(self.constituents) == set(other.constituents)

    def __mul__(self, other):
        raise NotImplementedError

    def __rmul__(self, other):
        return SimpleFunction(*map(lambda x: other * x, self.constituents))

    def __add__(self, other):
        if isinstance(other, SimpleFunction):
            result = SimpleFunction(*self.constituents)
            for char_func in other.constituents:
                result += char_func
            return result
        if isinstance(other, CharacteristicFunction):
            intersecting_functions = []

            for existing_func in self.constituents:
                if existing_func.domain.intersects(other.domain):
                    intersecting_functions.append(existing_func)
            new_domain = other.domain
            new_linear_combo = list(self.constituents)
            for intersecting_func in intersecting_functions:
                new_linear_combo.remove(intersecting_func)
                new_linear_combo.append(CharacteristicFunction(
                    new_domain * intersecting_func.domain,
                    other.coefficient + intersecting_func.coefficient
                ))
                for remainder in intersecting_func.domain - new_domain:
                    new_linear_combo.append(CharacteristicFunction(
                        remainder, intersecting_func.coefficient
                    ))
                new_domain *= intersecting_func.domain
            new_linear_combo.append(CharacteristicFunction(
                new_domain, other.coefficient
            ))
            return SimpleFunction(*new_linear_combo)
        raise NotImplementedError

    def __matmul__(self, other):
        raise NotImplementedError

    def evaluate(self, x: Numeric) -> Numeric:
        if len(self.constituents) == 0:
            return 0
        return FunctionSum(*self.constituents).evaluate(x)
