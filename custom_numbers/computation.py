from __future__ import annotations
from decimal import Decimal
from math import inf, isinf
from typing import TypeVar

from custom_numbers.types import Numeric
from custom_numbers.utils import gcd


rational_tol = 1000000000000000


class RationalNumber:
    @staticmethod
    def from_float(f: float):
        if f < 0:
            return -Number.of_float(-f)
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

    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise NotImplementedError
        if denominator > rational_tol:
            self.numerator, self.denominator = Decimal(str(
                numerator / denominator
            )).as_integer_ratio()
            return
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
        raise NotImplementedError

    def __sub__(self, other):
        return -(-self + other)

    def __rsub__(self, other):
        return -self + other

    def flip(self) -> RationalNumber:
        return RationalNumber(
            self.denominator,
            self.numerator,
        )

    def __truediv__(self, other):
        return self * self.resolve(other).flip()

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

    def to_decimal(self) -> Decimal:
        return Decimal(self.numerator) / Decimal(self.denominator)


T = TypeVar('T', Decimal, RationalNumber)


class Number:
    @staticmethod
    def float_to_dec(f: float):
        if isinf(f):
            return None

        return Decimal(str(f))

    @staticmethod
    def of_float(f: float):
        if isinf(f):
            if f < 0:
                return Number(inf_type=-1)
            return Number(inf_type=1)
        return Number(Decimal(str(f)))

    @staticmethod
    def of(x: Numeric):
        if isinstance(x, Decimal):
            return Number(x)
        if isinstance(x, Number):
            return Number(x.d, x.inf_type)
        if isinstance(x, int):
            return Number(Decimal(x))
        if isinstance(x, float):
            return Number.of_float(x)
        if isinstance(x, RationalNumber):
            return Number(x.to_decimal())

    @staticmethod
    def parse(s: str):
        if s == 'inf':
            return Number.of_float(inf)
        if s == '-inf':
            return Number.of_float(-inf)
        return Number.of(Decimal(s))

    def __init__(
        self, d: Decimal = None,
        inf_type: int = 0
    ):
        self.inf_type = inf_type
        self.d: Decimal = d

    def __str__(self):
        if self.inf_type != 0:
            return 'inf' if self.inf_type > 0 else '-inf'
        return str(self.d)

    def __repr__(self):
        return f'Number(d={self.d},inf_type={self.inf_type})'

    def __add__(self, other):
        if self.inf_type != 0:
            return Number(inf_type=self.inf_type)
        if isinstance(other, Number):
            return self + other.d
        if isinstance(other, RationalNumber):
            return Number(self.d + other.to_decimal())
        return Number(self.d + other)

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if self.inf_type != 0:
            if other == 0:
                return Number(Decimal(0))
            if other < 0:
                return Number(inf_type=-self.inf_type)
            return Number(inf_type=self.inf_type)
        if isinstance(other, Number):
            return Number(self.d * other.d)
        if isinstance(other, Numeric):
            return self * Number.of(other)
        return other.__rmul__(self)

    def __rmul__(self, other):
        return self * other

    def __pow__(self, power, modulo=None):
        if self.inf_type != 0:
            raise NotImplementedError
        if isinstance(power, Number):
            return Number(pow(self.d, power.d, modulo))
        return pow(self, Number.of(power), modulo)

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -(self + -other)

    def __truediv__(self, other):
        if self.inf_type != 0:
            return Number(None, self.inf_type)
        if isinstance(other, Number):
            if other.inf_type != 0:
                return Number.of(0)
            return Number(self.d / other.d)
        if isinstance(other, RationalNumber):
            return Number(self.d * other.flip().to_decimal())
        return Number(self.d / other)

    def __rtruediv__(self, other):
        if isinstance(other, RationalNumber):
            return Number(other.to_decimal() / self.d)
        return Number.of(other) / self

    def __eq__(self, other):
        if isinstance(other, Number):
            return other == self.d
        if self.inf_type != 0:
            if isinstance(other, Number):
                return self.inf_type * other.inf_type > 0
            if isinstance(other, float) and isinf(other):
                return self.inf_type < 0 and other < 0 \
                    or self.inf_type > 0 and other > 0
            return False

        return self.d == other

    def __hash__(self):
        if self.inf_type != 0:
            return hash(inf if self.inf_type > 0 else -inf)
        return hash(self.d)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if self.inf_type != 0:
            return self.inf_type < 0
        if isinstance(other, Number):
            if other.inf_type != 0:
                return other.inf_type > 0
            return self.d < other.d
        if isinstance(other, RationalNumber):
            return self.d < other.to_decimal()
        return self.d < other

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return -self < -other

    def __ge__(self, other):
        return self == other or self > other

    def __neg__(self):
        return Number(
            None if self.d is None else -self.d,
            -self.inf_type
        )

    def __abs__(self):
        return Number(
            None if self.d is None else abs(self.d),
            abs(self.inf_type)
        )

    def __round__(self, n: int = None):
        if self.inf_type != 0:
            return self
        # noinspection PyTypeChecker
        return Number(round(self.d, n))
