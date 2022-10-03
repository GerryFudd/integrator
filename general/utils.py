from __future__ import annotations
from abc import abstractmethod
from decimal import Decimal
from typing import Protocol, runtime_checkable


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
    def __sub__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __truediv__(self, other):
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


class RationalNumber:
    @staticmethod
    def from_float(f: float):
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
        self.numerator = int(numerator / c)
        self.denominator = int(denominator / c)

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
                False,
            )
        return RationalNumber.from_dec(pow(
            Decimal(str(self)), Decimal(str(power)), modulo
        ))

    def __sub__(self, other):
        return -(-self + other)

    def __rsub__(self, other):
        return -self + other

    def __truediv__(self, other):
        return ((self ** -1) * other) ** -1

    def __rtruediv__(self, other):
        return (self ** -1) * other

    def __repr__(self):
        return f'RationalNumber(numerator={self.numerator}, denominator=' \
               f'{self.denominator})'

    def __eq__(self, other):
        comparator = self.resolve(other)
        return self.numerator == comparator.numerator \
            and self.denominator == comparator.denominator

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return (self - other).numerator < 0

    def __le__(self, other):
        return (self - other).numerator <= 0

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


def minimum(a, b):
    if a <= b:
        return a
    return b


def maximum(a, b):
    if a >= b:
        return a
    return b


def vector_sum(l1, l2):
    result = []
    for i in range(maximum(len(l1), len(l2))):
        if len(l1) <= i:
            result.append(l2[i])
        elif len(l2) <= i:
            result.append(l1[i])
        else:
            result.append(l1[i] + l2[i])
    return result
