from __future__ import annotations
from decimal import Decimal
from math import inf, isinf
from typing import TypeVar

from custom_numbers.exact import ExactNumber, RationalNumber
from custom_numbers.types import Numeric


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
        return Number(Decimal(s))

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


NumberType = TypeVar('NumberType', Number, ExactNumber)
