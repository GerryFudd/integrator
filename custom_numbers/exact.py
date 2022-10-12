from __future__ import annotations

from abc import ABC
from decimal import Decimal
from typing import Callable

from custom_numbers.types import Numeric, N, ConvertableNumberABC
from custom_numbers.utils import gcd


class ExactNumber(ConvertableNumberABC, ABC):
    @staticmethod
    def do_for_builtins(
        other,
        action: Callable[[ExactNumber], ExactNumber],
        or_else: Callable[[], any]
    ):
        if isinstance(other, int) \
            or isinstance(other, float) \
                or isinstance(other, Decimal):
            return action(RationalNumber.of(other))
        return or_else()


class ExactZero(ExactNumber):
    def to_decimal(self) -> Decimal:
        return Decimal(0)

    @staticmethod
    def of(x: Numeric) -> N:
        raise NotImplementedError

    def __str__(self):
        return '0'

    def __add__(self, other):
        return other

    def __radd__(self, other):
        return other

    def __mul__(self, other):
        return self

    def __rmul__(self, other):
        return self

    def __pow__(self, power, modulo=None):
        if power <= 0:
            raise ArithmeticError
        return self

    def __sub__(self, other):
        return -other

    def __truediv__(self, other):
        return self

    def __rtruediv__(self, other):
        raise ArithmeticError

    def __eq__(self, other):
        return other == 0

    def __hash__(self):
        return hash(0)

    def __ne__(self, other):
        return other != 0

    def __lt__(self, other):
        return other > 0

    def __le__(self, other):
        return other >= 0

    def __gt__(self, other):
        return other < 0

    def __ge__(self, other):
        return other <= 0

    def __neg__(self):
        return self

    def __abs__(self):
        return self


class RationalNumber(ExactNumber):
    @staticmethod
    def from_float(f: float):
        if f < 0:
            return -RationalNumber.from_float(-f)
        numerator = int(f)
        denominator = 1
        r = f - numerator
        n = 0
        while r > 0 and n < 12:
            n += 1
            numerator = numerator << 4
            denominator = denominator << 4
            r *= 16
            numerator += int(r)
            r = r % 1
        if r > 0:
            return None
        return RationalNumber(numerator, denominator)

    @staticmethod
    def from_dec(dec: Decimal):
        return RationalNumber(*dec.as_integer_ratio())

    @staticmethod
    def from_dec_str(dec_str: str):
        return RationalNumber.from_dec(Decimal(dec_str))

    @staticmethod
    def of(x: Numeric) -> RationalNumber:
        if isinstance(x, ExactZero):
            return RationalNumber()
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
        return NotImplemented

    def __init__(self, numerator: int = 0, denominator: int = 1):
        if denominator == 0:
            raise NotImplementedError
        if denominator > 1000000000000:
            self.numerator, self.denominator = Decimal(str(
                numerator / denominator
            )).as_integer_ratio()
            return
        c = gcd(numerator, denominator)
        if denominator < 0:
            c = -c
        self.numerator = numerator // c
        self.denominator = denominator // c

    def to_decimal(self) -> Decimal:
        return Decimal(self.numerator) / Decimal(self.denominator)

    def flip(self) -> RationalNumber:
        return RationalNumber(
            self.denominator,
            self.numerator,
        )

    def __str__(self):
        if self.denominator == 1:
            return str(self.numerator)
        return str(self.to_decimal())

    def __add__(self, other):
        if not isinstance(other, RationalNumber) \
                and isinstance(other, ExactNumber):
            return other + self
        summand = self.of(other)
        new_denominator = self.denominator * summand.denominator
        new_numerator = self.numerator * summand.denominator \
            + summand.numerator * self.denominator
        return RationalNumber(new_numerator, new_denominator)

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        multiplicand = self.of(other)
        return RationalNumber(
            self.numerator * multiplicand.numerator,
            self.denominator * multiplicand.denominator,
            )

    def __rmul__(self, other):
        return self * other

    def __pow__(self, power, modulo=None):
        exponent = self.of(power)
        if exponent.denominator == 1 and not modulo:
            if exponent.numerator < 0:
                return RationalNumber(self.denominator, self.numerator) \
                       ** -exponent
            return RationalNumber(
                self.numerator ** exponent.numerator,
                self.denominator ** exponent.numerator,
                )
        raise NotImplementedError

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    def __truediv__(self, other):
        return self * self.of(other).flip()

    def __rtruediv__(self, other):
        return self.flip() * other

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
        return hash(self.to_decimal())

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
        return RationalNumber(-self.numerator, self.denominator)

    def __abs__(self):
        if self.numerator >= 0:
            return RationalNumber(self.numerator, self.denominator)
        return -self

    def __round__(self, n=None):
        new_denominator = 10 ** n
        new_numerator, remainder = divmod(
            self.numerator * new_denominator, self.denominator
        )
        if remainder * 2 >= self.denominator:
            new_numerator += 1
        return RationalNumber(new_numerator, new_denominator)
