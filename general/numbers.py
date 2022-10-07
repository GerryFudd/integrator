from __future__ import annotations
from abc import abstractmethod
from decimal import Decimal
from math import inf, isinf
from typing import runtime_checkable, Protocol


def minimum(a, b):
    if a <= b:
        return a
    return b


def maximum(a, b):
    if a >= b:
        return a
    return b


@runtime_checkable
class Numeric(Protocol):
    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __mul__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rmul__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __pow__(self, power, modulo=None):
        raise NotImplementedError

    @abstractmethod
    def __sub__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __truediv__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rtruediv__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __ne__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __le__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __gt__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __ge__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __neg__(self):
        raise NotImplementedError

    @abstractmethod
    def __abs__(self):
        raise NotImplementedError


def gcd(a: int, b: int):
    if a < 0 or b < 0:
        return gcd(abs(a), abs(b))
    if a == 0:
        return b
    if b == 0:
        return a

    n = maximum(a, b)
    m = minimum(a, b)

    return gcd(m, n % m)


def newton_int_sqrt(x: int):
    if x == 0:
        return 0
    if x < 0:
        raise NotImplementedError
    candidate = x

    while True:
        next_candidate = (candidate + x // candidate) // 2
        if abs(candidate - next_candidate) <= 1:
            return next_candidate
        candidate = next_candidate


class RationalNumber:
    @staticmethod
    def from_float(f: float):
        if isinf(f):
            raise NotImplementedError
        if f < 0:
            return -RationalNumber.from_float(abs(f))
        numerator = int(f // 1)
        r = f - numerator
        p = 0
        denominator = 1
        while r != 0 and p < 8:
            numerator = numerator * 16
            r = r * 16
            place = int(r // 1)
            r = r - place
            numerator += place
            p += 1
            denominator = 16 ** p
        return RationalNumber(numerator, denominator)

    @staticmethod
    def from_dec(dec: Decimal):
        return RationalNumber(*dec.as_integer_ratio())

    @staticmethod
    def from_dec_str(dec_str: str):
        return RationalNumber.from_dec(Decimal(dec_str))

    @staticmethod
    def resolve(x) -> RationalNumber:
        if isinstance(x, str):
            return RationalNumber.from_dec_str(x)
        if isinstance(x, RationalNumber):
            return x
        if isinstance(x, int):
            return RationalNumber(x)
        if isinstance(x, float):
            return RationalNumber.from_float(x)
        if isinstance(x, Decimal):
            return RationalNumber.from_dec(x)
        raise NotImplementedError

    def __init__(
        self, numerator: int, denominator: int = 1, reduce: bool = True
    ):
        if denominator == 0:
            raise NotImplementedError
        c = 1
        if reduce:
            c = gcd(numerator, denominator)
            if denominator < 0:
                c = -c
        self.numerator = numerator // c
        self.denominator = denominator // c

    def __str__(self):
        if self.denominator == 1:
            return str(self.numerator)
        return str(self.numerator / self.denominator)

    def __add__(self, other):
        summand = self.resolve(other)
        new_denominator = self.denominator * summand.denominator
        new_numerator = self.numerator * summand.denominator \
                        + summand.numerator * self.denominator
        return RationalNumber(new_numerator, new_denominator)

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        multiplicand = self.resolve(other)
        return RationalNumber(
            self.numerator * multiplicand.numerator,
            self.denominator * multiplicand.denominator,
            )

    def __rmul__(self, other):
        return self * other

    def __pow__(self, power, modulo=None):
        exponent = self.resolve(power)
        if exponent.denominator == 1 and not modulo:
            if exponent.numerator < 0:
                return RationalNumber(self.denominator, self.numerator) \
                       ** -exponent
            return RationalNumber(
                self.numerator ** exponent.numerator,
                self.denominator ** exponent.numerator,
            )
        if exponent.denominator == 2 and not modulo:
            return newton_sqrt(self ** exponent.numerator)
        return RationalNumber.from_dec(pow(
            self.to_decimal(), exponent.to_decimal(), modulo
        ))

    def __sub__(self, other):
        return -(-self + other)

    def __rsub__(self, other):
        return -self + other

    def __truediv__(self, other):
        return self * (self.resolve(other) ** -1)

    def __rtruediv__(self, other):
        return (self ** -1) * other

    def __repr__(self):
        return f'RationalNumber(numerator={self.numerator}, denominator=' \
               f'{self.denominator})'

    def __eq__(self, other):
        if isinstance(other, RationalNumber):
            return self.numerator * other.denominator == \
                   self.denominator * other.numerator
        return self.numerator == self.denominator * other

    def __req__(self, other):
        return self == other

    def __hash__(self):
        if self.denominator == 1:
            return hash(self.numerator)
        return hash(self.numerator / self.denominator)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.numerator < self.denominator * other

    def __le__(self, other):
        return self.numerator <= self.denominator * other

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    def __neg__(self):
        return RationalNumber(-1 * self.numerator, self.denominator, False)

    def __abs__(self):
        if self.numerator >= 0:
            return RationalNumber(self.numerator, self.denominator, False)
        return -self

    def __round__(self, n=None):
        return RationalNumber(
            self.numerator * 10 ** n // self.denominator,
            10 ** n
        )

    def to_decimal(self):
        return Decimal(self.numerator) / self.denominator


tol_inv = 1000000000000


def newton_sqrt(x: RationalNumber):
    if x.numerator == 0:
        return 0
    if x < 0:
        raise NotImplementedError
    candidate = RationalNumber(
        newton_int_sqrt(x.numerator),
        newton_int_sqrt(x.denominator)
    )

    while True:
        next_candidate = (candidate + x / candidate) / 2
        n = candidate.numerator * next_candidate.denominator * tol_inv
        d = candidate.denominator * next_candidate.denominator
        c = next_candidate.numerator * candidate.denominator * tol_inv
        if n - d <= c <= n + d:
            return next_candidate
        candidate = next_candidate


def resolve(string: str):
    if string == '-inf':
        return -inf
    if string == 'inf':
        return inf
    else:
        return RationalNumber.resolve(string)
