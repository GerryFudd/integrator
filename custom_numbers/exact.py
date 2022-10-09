from __future__ import annotations

from typing import Dict, Tuple, List

from custom_numbers.computation import Number, RationalNumber
from custom_numbers.types import Numeric
from custom_numbers.utils import gcd


class PrimeFactorization:
    def __init__(self, factors: Dict[int, int]):
        self.factors = factors

    def exact_root(self, n: int) -> Tuple[int, int]:
        if n < 1:
            raise NotImplementedError
        result = 1
        remainder = 1
        for key, val in self.factors.items():
            res_pow, rem_pow = divmod(val, n)
            result *= key ** res_pow
            remainder *= key ** rem_pow
        return result, remainder


def next_prime(max_val: int, sorted_odd_primes: List[int]) -> int:
    if len(sorted_odd_primes) == 0:
        return 3
    candidate = sorted_odd_primes[-1] + 2
    while candidate <= max_val:
        is_prime = True
        for p in sorted_odd_primes:
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            return candidate
        candidate += 2


def factor(n: int) -> PrimeFactorization:
    remainder = n
    x = 2
    odd_primes = []
    factors = {2: 0}
    while remainder > 1:
        next_remainder, test = divmod(remainder, x)
        if test == 0:
            factors[x] += 1
            remainder = next_remainder
            continue
        x = next_prime(remainder, odd_primes)
        odd_primes.append(x)
        factors[x] = 0
    return PrimeFactorization(factors)


class RadicalTerm:
    @staticmethod
    def of(
        coefficient: Numeric,
        root: int = 1,
        content: RationalNumber = RationalNumber(1),
    ):
        return RadicalTerm(RationalNumber.resolve(coefficient), root, content).__reduce()

    def __init__(
        self,
        coefficient: RationalNumber,
        root: int = 1,
        content: RationalNumber = RationalNumber(1),
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
    def __rational_str(x: RationalNumber) -> Tuple[str, str]:
        denom_string = f'/{x.denominator}' \
            if x.denominator != 1 else ''
        return str(x.numerator), denom_string

    def __str__(self):
        cfn, cfd = self.__rational_str(self.coefficient)
        if self.root == 1:
            return f'{cfn}{cfd}'
        cnn, cnd = self.__rational_str(self.content)
        return f'{cfn}({cnn}{cnd})^(1/{self.root}){cfd}'

    def __repr__(self):
        cfn, cfd = self.__rational_str(self.coefficient)
        cnn, cnd = self.__rational_str(self.content)
        return f'RadicalTerm(coefficient={cfn}{cfd},root={self.root},' \
               f'content={cnn}{cnd})'

    def __reduce(self) -> RadicalTerm:
        coeff_num, content_num = factor(
            self.content.numerator,
        ).exact_root(self.root)
        coeff_denom, content_denom = factor(
            self.content.denominator,
        ).exact_root(self.root)
        return RadicalTerm(
            self.coefficient * RationalNumber(coeff_num, coeff_denom),
            self.root, RationalNumber(content_num, content_denom),
        )

    def flip(self) -> RadicalTerm:
        return RadicalTerm(
            self.coefficient.flip(), self.root, self.content.flip(),
        )

    def to_number(self) -> Number:
        return self.content.to_decimal() \
               ** RationalNumber(1, self.root).to_decimal() \
               * self.coefficient.to_decimal()

    def __add__(self, other):
        if isinstance(other, RadicalTerm) \
                and self.root == other.root \
                and self.content == other.content:
            return RadicalTerm(
                self.coefficient + other.coefficient,
                self.root, self.content,
            )
        if self.root == 1 and isinstance(other, RationalNumber):
            return RadicalTerm(
                self.content + other
            )
        return other.__radd__(self)

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
            )
        if isinstance(other, RationalNumber):
            return RadicalTerm(
                self.coefficient * other,
                self.root, self.content,
            )
        return other.__rmul__(self)

    def __rmul__(self, other):
        if isinstance(other, RationalNumber):
            return self * other
        return other.__mul__(self)

    def __pow__(self, power, modulo=None):
        if isinstance(power, int) and modulo is None:
            return self ** RationalNumber(power)
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
        raise NotImplementedError

    def __sub__(self, other):
        return -self + other

    def __truediv__(self, other):
        if isinstance(other, RationalNumber):
            return self * RationalNumber(other.denominator, other.numerator)
        if isinstance(other, RadicalTerm):
            return self * other.flip()
        return other.__rmul__(self)

    def __rtruediv__(self, other):
        return self.flip() * other

    def __hash__(self):
        return hash(self.to_number())

    def __eq__(self, other):
        if isinstance(other, RadicalTerm):
            return self.root == other.root \
                   and self.coefficient == other.coefficient \
                   and self.content == other.content
        if self.root == 1:
            return self.coefficient == other
        return False

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if isinstance(other, RadicalTerm):
            return self < other.to_number()
        return self.to_number() < other

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


class ExactNumber:
    @staticmethod
    def of(x: Numeric):
        if isinstance(x, ExactNumber):
            return x
        if isinstance(x, RadicalTerm):
            return ExactNumber(x)
        return ExactNumber(RadicalTerm.of(x))

    def __init__(self, *radical_terms: RadicalTerm):
        if len(radical_terms) == 0:
            self.radical_terms = [RadicalTerm(RationalNumber(0))]
            return
        self.radical_terms = list(radical_terms)

    def to_number(self) -> Numeric:
        return sum(map(lambda x: x.to_number(), self.radical_terms), Number.of(0))

    def __str__(self):
        return ' + '.join(map(str, self.radical_terms))

    def __repr__(self):
        return f'ExactNumber({",".join(map(str, self.radical_terms))})'

    def __add__(self, other):
        if isinstance(other, RadicalTerm):
            result_terms = []
            for radical_term in self.radical_terms:
                if radical_term.root == other.root \
                        and radical_term.content == other.content:
                    t = radical_term + other
                    if t != RationalNumber(0):
                        result_terms.append(t)
                    continue
                result_terms.append(radical_term)
            return ExactNumber(*result_terms)
        if isinstance(other, ExactNumber):
            return sum(other.radical_terms, self)
        return self + RadicalTerm.of(other)

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if isinstance(other, RadicalTerm):
            return sum(map(
                lambda x: x * other, self.radical_terms
            ), ExactNumber())
        if isinstance(other, ExactNumber):
            return sum(map(
                lambda x: self * x, other.radical_terms
            ), ExactNumber())
        if isinstance(other, Numeric):
            return self * RadicalTerm.of(other)
        return other.__rmul__(self)

    def __rmul__(self, other):
        return self * other

    def __pow__(self, power, modulo=None):
        if isinstance(power, int):
            result = ExactNumber.of(1)
            n = 0
            while n < power:
                n += 1
                result *= self
            return result
        if isinstance(power, RationalNumber):
            if len(self.radical_terms) == 1:
                return ExactNumber(self.radical_terms[0] ** power)
            if power.denominator == 1:
                return self ** power.numerator
        if isinstance(power, float):
            return self ** RationalNumber.from_float(power)
        raise NotImplementedError

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    def __truediv__(self, other):
        if isinstance(other, ExactNumber):
            if len(other.radical_terms) > 1:
                raise NotImplementedError
            return self / other.radical_terms[0]
        if isinstance(other, RadicalTerm):
            return self * other.flip()

        return self / RadicalTerm.of(other)

    def __rtruediv__(self, other):
        if len(self.radical_terms) == 1:
            return ExactNumber(self.radical_terms[0].flip()) * other
        raise NotImplementedError

    def __eq__(self, other):
        if isinstance(other, ExactNumber):
            return set(self.radical_terms) == set(other.radical_terms)
        if len(self.radical_terms) == 1:
            return self.radical_terms[0] == other
        return False

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if isinstance(other, ExactNumber):
            return self < other.to_number()
        return self.to_number() < other

    def __le__(self, other):
        if isinstance(other, ExactNumber):
            return self <= other.to_number()
        return self.to_number() <= other

    def __gt__(self, other):
        return -self < -other

    def __ge__(self, other):
        return -self <= -other

    def __neg__(self):
        return ExactNumber(*map(lambda x: -x, self.radical_terms))

    def __abs__(self):
        if self < 0:
            return -self
        return self
