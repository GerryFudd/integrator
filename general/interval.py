from __future__ import annotations

from general.numbers import maximum, minimum, Numeric, resolve


class Interval:
    @staticmethod
    def parse(string: str):
        opening_bracket = string[0]
        if opening_bracket not in ['[', '(']:
            raise NotImplementedError
        include_left = opening_bracket == '['
        closing_bracket = string[-1]
        if closing_bracket not in [']', ')']:
            raise NotImplementedError
        include_right = closing_bracket == ']'
        parts = string[1:-1].split(',')
        if len(parts) != 2:
            raise NotImplementedError
        return Interval(
            resolve(parts[0].strip()),
            resolve(parts[1].strip()),
            include_left, include_right
        )

    def __init__(
        self, a: Numeric, b: Numeric,
        include_left: bool = False,
        include_right: bool = False,
    ):
        if b < a:
            raise NotImplementedError
        self.a = a
        self.b = b
        self.include_left = include_left
        self.include_right = include_right

    def __str__(self):
        left_boundary = '[' if self.include_left else '('
        right_boundary = ']' if self.include_right else ')'
        return f'{left_boundary}{self.a},{self.b}{right_boundary}'

    def __repr__(self):
        return f'Interval(left={self.a},right={self.b},' \
               f'include_left={self.include_left},' \
               f'include_right={self.include_right})'

    def __lt__(self, other):
        if not isinstance(other, Interval):
            raise NotImplementedError
        return self.a < other.a \
            or (
                   self.a == other.a
                   and self.include_left
                   and not other.include_left
               ) \
            or (self.a == other.a and self.b < other.b) \
            or (
                   self.a == other.a
                   and self.b == other.b
                   and not self.include_right
                   and other.include_right
               )

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
        return self.a == other.a \
            and self.b == other.b \
            and self.include_left == other.include_left \
            and self.include_right == other.include_right

    def __hash__(self):
        return hash((self.a, self.b, self.include_left, self.include_right))

    def __ne__(self, other):
        return not (self == other)

    def __copy__(self):
        return Interval(
            self.a, self.b, self.include_left, self.include_right
        )

    def measure(self):
        return self.b - self.a

    def intersects(self, interval: Interval) -> bool:
        return self.a < interval.b and interval.a < self.b

    def contains(self, x: Numeric) -> bool:
        if self.a == x:
            return self.include_left
        if self.b == x:
            return self.include_right
        return self.a < x < self.b

    def __add__(self, other):
        if not isinstance(other, Interval) or not self.intersects(other):
            raise NotImplementedError
        c = minimum(self.a, other.a)
        d = maximum(self.b, other.b)
        include_left = False
        include_right = False
        if (self.include_left and c == self.a) \
                or (other.include_left and c == other.a):
            include_left = True
        if (self.include_right and d == self.b) \
                or (other.include_right and d == other.b):
            include_right = True

        return Interval(
            minimum(self.a, other.a),
            maximum(self.b, other.b),
            include_left=include_left,
            include_right=include_right,
        )

    def __sub__(self, other):
        if not isinstance(other, Interval):
            raise NotImplementedError

        if not self.intersects(other):
            return [self.__copy__()]
        result = []
        if self.a < other.a:
            result.append(Interval(
                self.a,
                other.a,
                self.include_left,
                not other.include_left
            ))
        if other.b < self.b:
            result.append(Interval(
                other.b,
                self.b,
                not other.include_right,
                self.include_right
            ))
        return result

    def __mul__(self, other):
        if not isinstance(other, Interval) or not self.intersects(other):
            raise NotImplementedError

        return Interval(
            maximum(self.a, other.a),
            minimum(self.b, other.b),
            include_left=self.include_left if self.a < other.a
            else other.include_left if other.a < self.a
            else self.include_left and other.include_left,
            include_right=self.include_right if other.b < self.b
            else other.include_right if self.b < other.b
            else self.include_right and other.include_right,
        )
