from __future__ import annotations

from abc import ABC
from decimal import Decimal

from custom_numbers.types import ConvertableNumberABC, Numeric, N


class ExactNumber(ConvertableNumberABC, ABC):
    pass


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
