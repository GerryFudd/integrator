from __future__ import annotations

from decimal import Decimal

from custom_numbers.exact.rational_number import RationalNumber
from custom_numbers.exact.types import ExactNumber
from custom_numbers.exact.utils import BaseExactNumber
from custom_numbers.radicals.factoring import factor
from custom_numbers.types import Numeric, FlippableNumber, Convertable
from custom_numbers.utils import gcd, maximum


class RadicalTerm(BaseExactNumber):
    coefficient: RationalNumber
    power: int
    content: ExactNumber

    @staticmethod
    def of(x: Numeric) -> RadicalTerm:
        if isinstance(x, RadicalTerm):
            return x
        return RadicalTerm(RationalNumber.of(x))

    @staticmethod
    def reduced(
        coefficient: Numeric,
        root: int = 1,
        content: ExactNumber = RationalNumber(1),
    ):
        return RadicalTerm(RationalNumber.of(coefficient), root, content)\
            .__reduce()

    def __init__(
        self,
        coefficient: RationalNumber,
        root: int = 1,
        content: ExactNumber = RationalNumber(1),
    ):
        if root < 1:
            raise NotImplementedError
        if content == 1:
            self.coefficient = coefficient
            self.root = 1
            self.content = content
            return
        if content == 0:
            self.coefficient = RationalNumber(0)
            self.root = 1
            self.content = RationalNumber(1)
            return

        self.root = root
        if root == 1:
            self.coefficient = coefficient * content
            self.content = RationalNumber(1)
            return
        if content < 0:
            if root % 2 == 0:
                raise NotImplementedError
            self.coefficient = -coefficient
            self.content = -content
            return
        self.coefficient = coefficient
        self.content = content

    @staticmethod
    def __rational_str(x: RationalNumber) -> tuple[str, str]:
        num_str = '' if x.numerator == 1 else str(x.numerator)
        denom_string = f'/{x.denominator}' \
            if x.denominator != 1 else ''
        return num_str, denom_string

    def __str__(self):
        cfn, cfd = self.__rational_str(self.coefficient)
        if self.root == 1:
            return f'{cfn}{cfd}'
        return f'{cfn}({self.content})^(1/{self.root}){cfd}'

    def __repr__(self):
        return f'RadicalTerm(coefficient={self.coefficient.numerator}/' \
               f'{self.coefficient.denominator},' \
               f'root={self.root},' \
               f'content={self.content})'

    def __reduce(self) -> RadicalTerm:
        if not isinstance(self.content, RationalNumber):
            return self

        new_root = 1
        factored_numerator = factor(self.content.numerator)
        factored_denominator = factor(self.content.denominator)

        for prime, multiplicity in factor(self.root):
            for n in range(multiplicity):
                reduced_numerator, numerator_root = factored_numerator\
                    .reduce(prime)
                reduced_denominator, denominator_root = factored_denominator\
                    .reduce(prime)
                if numerator_root == denominator_root:
                    new_root *= numerator_root
                    factored_numerator = reduced_numerator
                    factored_denominator = reduced_denominator
                else:
                    new_root *= maximum(numerator_root, denominator_root)

        coeff_num, content_num = factored_numerator.exact_root(new_root)
        coeff_denom, content_denom = factored_denominator.exact_root(new_root)
        return RadicalTerm(
            self.coefficient * RationalNumber(coeff_num, coeff_denom),
            new_root, RationalNumber(content_num, content_denom),
        )

    def to_decimal(self) -> Decimal:
        return self.content.to_decimal() \
               ** RationalNumber(1, self.root).to_decimal() \
               * self.coefficient.to_decimal()

    def __add__(self, other):
        if isinstance(other, RadicalTerm):
            if self.root == other.root \
                    and self.content == other.content:
                return RadicalTerm(
                    self.coefficient + other.coefficient,
                    self.root, self.content,
                )
            return NotImplemented
        if self.root != 1:
            return other.__radd__(self)

        return self.do_for_builtins(
            other,
            lambda x: self + x,
            lambda: other.__radd__(self)
        )

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if isinstance(other, RadicalTerm):
            d = gcd(self.root, other.root)
            return RadicalTerm(
                self.coefficient * other.coefficient,
                self.root * other.root // d,
                self.content ** (other.root // d)
                * other.content ** (self.root // d)
            ).__reduce()
        if isinstance(other, RationalNumber):
            return RadicalTerm(
                self.coefficient * other,
                self.root, self.content,
            ).__reduce()
        self.do_for_builtins(
            other,
            lambda x: self * x,
            lambda: other.__rmul__(self)
        )

    def __rmul__(self, other):
        if isinstance(other, RationalNumber):
            return self * other
        return other.__mul__(self)

    def __pow__(self, power, modulo=None):
        if isinstance(power, RationalNumber) and modulo is None:
            e = power / self.root

            return (RadicalTerm(
                RationalNumber(1),
                power.denominator,
                self.coefficient ** power.numerator
            ) * RadicalTerm(
                RationalNumber(1),
                e.denominator,
                self.content ** e.numerator
            )).__reduce()
        return self.do_for_builtins(
            power,
            lambda x: pow(self, x, modulo),
            lambda: NotImplemented
        )

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    def __truediv__(self, other):
        if isinstance(other, RationalNumber):
            return self * other.flip()
        if isinstance(other, RadicalTerm):
            d = gcd(self.root, other.root)
            return RadicalTerm(
                self.coefficient / other.coefficient,
                self.root * other.root // d,
                self.content ** (other.root // d)
                / other.content ** (self.root // d)
            )
        return self.do_for_builtins(
            other,
            lambda x: self / x,
            lambda: other.__rmul__(self),
        )

    def __rtruediv__(self, other):
        if isinstance(self.content, FlippableNumber):
            return RadicalTerm(
                self.coefficient.flip(),
                self.root,
                self.content.flip(),
            ) * other
        return other.__truediv__(self)

    def __eq__(self, other):
        if isinstance(other, RadicalTerm):
            return self.root == other.root \
                   and self.coefficient == other.coefficient \
                   and self.content == other.content
        if self.root == 1:
            return self.coefficient == other
        return False

    def __hash__(self):
        return hash(self.to_decimal())

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if isinstance(other, Convertable):
            return self < other.to_decimal()
        return self.to_decimal() < other

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return self == other or self > other

    def __neg__(self):
        return RadicalTerm(-self.coefficient, self.root, self.content)

    def __abs__(self):
        return RadicalTerm(abs(self.coefficient), self.root, self.content)
