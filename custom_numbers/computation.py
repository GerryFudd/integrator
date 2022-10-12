from __future__ import annotations

from decimal import Decimal
from math import inf, isinf
from typing import Callable

from custom_numbers.types import Numeric, Convertable


class DecimalNumber(Convertable):
    @staticmethod
    def of(x: Numeric) -> DecimalNumber:
        if isinstance(x, Decimal):
            return DecimalNumber(x)
        if isinstance(x, DecimalNumber):
            return DecimalNumber(x.d, x.inf_type)
        if isinstance(x, int):
            return DecimalNumber(Decimal(x))
        if isinstance(x, float):
            return DecimalNumber.of_float(x)
        if isinstance(x, Convertable):
            return DecimalNumber(x.to_decimal())

    @staticmethod
    def float_to_dec(f: float):
        if isinf(f):
            return None

        return Decimal(str(f))

    @staticmethod
    def of_float(f: float):
        if isinf(f):
            if f < 0:
                return DecimalNumber(inf_type=-1)
            return DecimalNumber(inf_type=1)
        return DecimalNumber(Decimal(str(f)))

    @staticmethod
    def parse(s: str):
        if s == 'inf':
            return DecimalNumber.of_float(inf)
        if s == '-inf':
            return DecimalNumber.of_float(-inf)
        return DecimalNumber(Decimal(s))

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

    def to_decimal(self) -> Decimal:
        if self.inf_type != 0:
            return NotImplemented
        return self.d

    @staticmethod
    def do_for_builtins(
        other,
        action: Callable[[int | Decimal], DecimalNumber],
        or_else: Callable[[], any]
    ):
        if isinstance(other, int) or isinstance(other, Decimal):
            return action(other)
        if isinstance(other, float):
            return action(DecimalNumber.float_to_dec(other))
        return or_else()

    def __add__(self, other):
        if self.inf_type != 0:
            return DecimalNumber(inf_type=self.inf_type)
        if isinstance(other, DecimalNumber):
            if other.inf_type != 0:
                return DecimalNumber(inf_type=other.inf_type)
            return DecimalNumber(self.d + other.d)
        return self.do_for_builtins(
            other,
            lambda x: DecimalNumber(self.d + x),
            lambda: other.__radd__(self)
        )

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if isinstance(other, DecimalNumber):
            if self.inf_type != 0:
                if other.inf_type != 0:
                    return DecimalNumber(
                        inf_type=self.inf_type * other.inf_type
                    )
                return DecimalNumber(other.d, self.inf_type * other.inf_type)
            return DecimalNumber(self.d * other.d)
        if self.inf_type != 0:
            if other == 0:
                return DecimalNumber(Decimal(0))
            if other < 0:
                return DecimalNumber(inf_type=-self.inf_type)
            return DecimalNumber(inf_type=self.inf_type)
        return self.do_for_builtins(
            other,
            lambda x: DecimalNumber(self.d * x),
            lambda: other.__rmul__(self)
        )

    def __rmul__(self, other):
        return self * other

    def __pow__(self, power, modulo=None):
        if self.inf_type != 0:
            raise NotImplementedError
        if isinstance(power, DecimalNumber):
            return DecimalNumber(pow(self.d, power.d, modulo))
        return self.do_for_builtins(
            power,
            lambda x: DecimalNumber(pow(self.d, Decimal(x), modulo)),
            lambda: NotImplemented
        )

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    def __truediv__(self, other):
        if self.inf_type != 0:
            return self
        if isinstance(other, DecimalNumber):
            if other.inf_type != 0:
                return DecimalNumber.of(0)
            return DecimalNumber(self.d / other.d)
        return self.do_for_builtins(
            other,
            lambda x: DecimalNumber(self.d / x),
            lambda _: other.__rtruediv__(self)
        )

    def __rtruediv__(self, other):
        if self.inf_type != 0:
            return DecimalNumber.of(0)
        return self.do_for_builtins(
            other,
            lambda x: DecimalNumber(x / self.d),
            lambda _: other.__truediv__(self)
        )

    def __eq__(self, other):
        if isinstance(other, DecimalNumber):
            if self.inf_type * other.inf_type < 0:
                return False
            return self.d == other.d

        if self.inf_type != 0:
            if isinstance(other, float) and isinf(other):
                return self.inf_type < 0 and other < 0 \
                       or self.inf_type > 0 and other > 0
            return False
        return other == self.d

    def __hash__(self):
        if self.inf_type != 0:
            return hash(inf if self.inf_type > 0 else -inf)
        return hash(self.d)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if self.inf_type != 0:
            return self.inf_type < 0
        if isinstance(other, DecimalNumber):
            if other.inf_type != 0:
                return other.inf_type > 0
            return self.d < other.d
        if isinstance(other, Convertable):
            return self.d < other.to_decimal()
        return self.d < other

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return -self < -other

    def __ge__(self, other):
        return self == other or self > other

    def __neg__(self):
        return DecimalNumber(
            None if self.d is None else -self.d,
            -self.inf_type
        )

    def __abs__(self):
        return DecimalNumber(
            None if self.d is None else abs(self.d),
            abs(self.inf_type)
        )

    def __round__(self, n: int = None):
        if self.inf_type != 0:
            return self
        # noinspection PyTypeChecker
        return DecimalNumber(round(self.d, n))
