from __future__ import annotations

from decimal import Decimal
from typing import List

from custom_numbers.exact.rational_number import RationalNumber
from custom_numbers.exact.utils import BaseExactNumber
from custom_numbers.radicals.radical_term import RadicalTerm
from custom_numbers.types import Numeric, FlippableNumber, \
    Convertable
from custom_numbers.utils import lcm


class RadicalSum(BaseExactNumber):
    @staticmethod
    def of(x: Numeric):
        if isinstance(x, RadicalSum):
            return x
        if isinstance(x, RadicalTerm):
            return RadicalSum(x)
        return RadicalSum(RadicalTerm.of(x))

    def __init__(self, *radical_terms: RadicalTerm):
        if len(radical_terms) == 0:
            self.radical_terms = [RadicalTerm(RationalNumber())]
            return
        self.radical_terms = list(radical_terms)

    def to_decimal(self) -> Decimal:
        return sum(
            map(lambda x: x.to_decimal(), self.radical_terms),
            Decimal(0)
        )

    def __str__(self):
        return ' + '.join(map(str, self.radical_terms))

    def __repr__(self):
        return f'RadicalSum({",".join(map(str, self.radical_terms))})'

    @staticmethod
    def __append_if_not_zero(terms: List[RadicalTerm], candidate: RadicalTerm):
        if candidate.coefficient != 0:
            terms.append(candidate)

    def __add__(self, other):
        if isinstance(other, RadicalTerm):
            result_terms = []
            other_used = False
            for radical_term in self.radical_terms:
                if not other_used and radical_term.root == other.root \
                        and radical_term.content == other.content:
                    t = RadicalTerm(
                        radical_term.coefficient + other.coefficient,
                        radical_term.root,
                        radical_term.content,
                    )
                    other_used = True
                    self.__append_if_not_zero(result_terms, t)
                    continue
                self.__append_if_not_zero(result_terms, radical_term)
            if not other_used:
                self.__append_if_not_zero(result_terms, other)
            return RadicalSum(*result_terms)
        if isinstance(other, RadicalSum):
            return sum(other.radical_terms, self)
        return self + RadicalTerm.of(other)

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if isinstance(other, RadicalTerm):
            return sum(map(
                lambda x: x * other, self.radical_terms
            ), RadicalSum.of(0))
        if isinstance(other, RadicalSum):
            return sum(map(
                lambda x: self * x, other.radical_terms
            ), RadicalSum.of(0))
        return self.do_for_builtins(
            other,
            lambda x: self * RadicalTerm(x),
            lambda: other.__rmul__(self),
        )

    def __rmul__(self, other):
        return self * other

    def __pow__(self, power, modulo=None):
        if isinstance(power, int):
            result = RadicalSum.of(1)
            n = 0
            while n < power:
                n += 1
                result *= self
            return result
        if isinstance(power, RationalNumber):
            if len(self.radical_terms) == 1:
                return RadicalSum(self.radical_terms[0] ** power)
            if power.denominator == 1:
                return self ** power.numerator
        if isinstance(power, float):
            return self ** RationalNumber.from_float(power)
        raise NotImplementedError

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    def limited_flip(self) -> RadicalSum:
        term_count = len(self.radical_terms)
        if term_count > 2:
            return NotImplemented
        first_term = self.radical_terms[0]
        if term_count == 1:
            if isinstance(first_term.content, FlippableNumber):
                return RadicalSum(RadicalTerm(
                    first_term.coefficient.flip(),
                    first_term.root,
                    first_term.content.flip()
                ))
        second_term = self.radical_terms[1]
        m = lcm(first_term.root, second_term.root)

        new_numerator_terms = []
        while len(new_numerator_terms) < m:
            b = len(new_numerator_terms)
            a = m - 1 - b
            new_numerator_terms.append(
                first_term ** a * (-second_term) ** b
            )
        new_numerator = RadicalSum(*new_numerator_terms)
        new_denominator = self * new_numerator
        return new_numerator / new_denominator

    def __truediv__(self, other):
        if isinstance(other, RadicalSum):
            return self * other.limited_flip()
        if isinstance(other, RadicalTerm):
            return sum(map(
                lambda x: x / other, self.radical_terms
            ), RadicalSum.of(0))

        return self / RadicalTerm.of(other)

    def __rtruediv__(self, other):
        return self.limited_flip() * other

    def __eq__(self, other):
        if isinstance(other, RadicalSum):
            return set(self.radical_terms) == set(other.radical_terms)
        if len(self.radical_terms) == 1:
            return self.radical_terms[0] == other
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
        if isinstance(other, Convertable):
            return self <= other.to_decimal()
        return self.to_decimal() <= other

    def __gt__(self, other):
        return -self < -other

    def __ge__(self, other):
        return -self <= -other

    def __neg__(self):
        return RadicalSum(*map(lambda x: -x, self.radical_terms))

    def __abs__(self):
        if self < 0:
            return -self
        return self
