from __future__ import annotations

from typing import List

from elementary_functions.utils import FunctionSum
from general.numbers import maximum, minimum, Numeric


class Interval:
    def __init__(self, a: Numeric, b: Numeric):
        if b < a:
            raise NotImplementedError
        self.a = a
        self.b = b

    def __str__(self):
        return f'({self.a},{self.b})'

    def __lt__(self, other):
        if not isinstance(other, Interval):
            raise NotImplementedError
        return self.a < other.a or (self.a == other.a and self.b < other.b)

    def __le__(self, other):
        if not isinstance(other, Interval):
            raise NotImplementedError
        return self < other or self == other

    def __gt__(self, other):
        if not isinstance(other, Interval):
            raise NotImplementedError
        return other < self

    def __ge__(self, other):
        if not isinstance(other, Interval):
            raise NotImplementedError
        return other < self or self == other

    def __eq__(self, other):
        if not isinstance(other, Interval):
            return False
        return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not (self == other)

    def measure(self):
        return self.b - self.a

    def intersects(self, interval: Interval) -> bool:
        return self.a < interval.b and interval.a < self.b

    def contains(self, x: Numeric) -> bool:
        return self.a < x < self.b

    def __add__(self, other):
        if not isinstance(other, Interval) or not self.intersects(other):
            raise NotImplementedError
        return Interval(
            minimum(self.a, other.a),
            maximum(self.b, other.b),
        )

    def __sub__(self, other):
        if not isinstance(other, Interval):
            raise NotImplementedError

        if not self.intersects(other):
            return [Interval(self.a, self.b)]
        result = []
        if self.a < other.a:
            result.append(Interval(self.a, other.a))
        if other.b < self.b:
            result.append(Interval(other.b, self.b))
        return result

    def __mul__(self, other):
        if not isinstance(other, Interval) or not self.intersects(other):
            raise NotImplementedError
        return Interval(
            maximum(self.a, other.a),
            minimum(self.b, other.b),
        )


class CharacteristicFunction:
    def __init__(self, domain: Interval, coefficient: Numeric = 1):
        self.domain = domain
        self.coefficient = coefficient

    def __str__(self):
        return f'{self.coefficient}X_{self.domain}'

    def evaluate(self, x: Numeric) -> Numeric:
        if self.domain.contains(x):
            return self.coefficient
        return 0

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


class SimpleFunction:
    def __init__(self, *linear_combo: CharacteristicFunction):
        self.constituents: List[CharacteristicFunction] = list(linear_combo)

    def __str__(self):
        return ' + '.join(map(
            str,
            filter(lambda x: x.coefficient != 0, self.constituents)
        ))

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

    def evaluate(self, x: Numeric) -> Numeric:
        if len(self.constituents) == 0:
            return 0
        return FunctionSum(*self.constituents).evaluate(x)
