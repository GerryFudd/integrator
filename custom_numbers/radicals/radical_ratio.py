from __future__ import annotations
from decimal import Decimal

from custom_numbers.exact.types import ExactNumber
from custom_numbers.exact.utils import BaseExactNumber
from custom_numbers.radicals.radical_sum import RadicalSum
from custom_numbers.types import Numeric, N


class RadicalRatio(BaseExactNumber):

    @staticmethod
    def of(x: Numeric) -> N:
        return RadicalRatio(RadicalSum.of(x), RadicalSum.of(1))

    def __init__(self, numerator: RadicalSum, denominator: RadicalSum):
        self.numerator = numerator
        self.denominator = denominator

    def to_decimal(self) -> Decimal:
        return self.numerator.to_decimal() / self.denominator.to_decimal()

    def flip(self) -> RadicalRatio:
        return RadicalRatio(self.denominator, self.numerator)

    def __str__(self):
        return f'({self.numerator})/({self.denominator})'

    def __repr__(self):
        return f'RadicalRatio(numerator={self.numerator},' \
               f'denominator={self.denominator})'

    def __reduce(self):
        return self

    def __add__(self, other):
        if isinstance(other, RadicalRatio):
            return RadicalRatio(
                self.numerator * other.denominator
                + other.numerator * self.denominator,
                self.denominator * other.denominator,
            ).__reduce()
        return RadicalRatio(
            self.numerator + self.denominator * other,
            self.denominator
        ).__reduce()

    def __radd__(self, other):
        if isinstance(other, ExactNumber):
            return self + other
        return self + RadicalSum.of(other)

    def __mul__(self, other):
        if isinstance(other, RadicalRatio):
            return RadicalRatio(
                self.numerator * other.numerator,
                self.denominator * other.denominator,
            ).__reduce()
        if isinstance(other, Numeric):
            return RadicalRatio(
                self.numerator * other,
                self.denominator
            ).__reduce()
        return other.__rmul__(self)

    def __rmul__(self, other):
        if isinstance(other, Numeric):
            return self * other
        return other.__mul__(self)

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError
        if power == 0:
            return self.of(1)
        if power < 0:
            return self.flip() ** -power
        return RadicalRatio(
            self.numerator ** power,
            self.denominator ** power,
        )

    def __sub__(self, other):
        return self + -other

    def __truediv__(self, other):
        if isinstance(other, RadicalRatio):
            return self * other.flip()
        if isinstance(other, Numeric):
            return RadicalRatio(self.numerator, self.denominator * other)
        return other.__rtruediv__(self)

    def __rtruediv__(self, other):
        return other * self.flip()

    def __eq__(self, other):
        if isinstance(other, RadicalRatio):
            return self.numerator * other.denominator \
                == other.numerator * self.denominator
        if isinstance(other, ExactNumber):
            return self.numerator == self.denominator * other
        return self == self.of(other)

    def __hash__(self):
        return hash(self.to_decimal())

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return other > self.to_decimal()

    def __le__(self, other):
        return other >= self.to_decimal()

    def __gt__(self, other):
        return other < self.to_decimal()

    def __ge__(self, other):
        return other <= self.to_decimal()

    def __neg__(self):
        return RadicalRatio(-self.numerator, self.denominator)

    def __abs__(self):
        if self < 0:
            return -self
        return self
