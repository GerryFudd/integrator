from __future__ import annotations

from abc import ABC
from decimal import Decimal
from typing import Dict, List

from custom_numbers.types import Numeric, Convertable, FlippableNumber, N, \
    ConvertableNumberABC
from custom_numbers.utils import gcd


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


rational_tol = 1000000000000000


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

    def to_decimal(self) -> Decimal:
        return Decimal(self.numerator) / Decimal(self.denominator)

    def to_float(self) -> float:
        return self.numerator / self.denominator

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


class PrimeFactorization:
    def __init__(self, factors: Dict[int, int]):
        self.factors = factors

    def exact_root(self, n: int) -> tuple[int, int]:
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


class RadicalTerm(ExactNumber):
    coefficient: RationalNumber
    power: int
    content: ExactNumber

    @staticmethod
    def of(x: Numeric):
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
        cfn, cfd = self.__rational_str(self.coefficient)
        return f'RadicalTerm(coefficient={cfn}{cfd},root={self.root},' \
               f'content={self.content})'

    def __reduce(self) -> RadicalTerm:
        if not isinstance(self.content, RationalNumber):
            return self
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

    def to_decimal(self) -> Decimal:
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
        if self.root == 1 and (
            isinstance(other, RationalNumber)
            or not isinstance(other, ExactNumber)
        ):
            return RadicalTerm(
                self.coefficient + RationalNumber.of(other)
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
        if isinstance(other, Numeric) and not isinstance(other, ExactNumber):
            return self * RationalNumber.of(other)
        return other.__rmul__(self)

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
        if isinstance(power, Numeric) and not isinstance(power, ExactNumber):
            return pow(self, RationalNumber.of(power), modulo)
        raise NotImplementedError

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
        if isinstance(other, Numeric) and not isinstance(other, ExactNumber):
            return self / RationalNumber.of(other)
        return other.__rmul__(self)

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


class RadicalSum(ExactNumber):
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

    def __add__(self, other):
        if isinstance(other, RadicalTerm):
            result_terms = []
            for radical_term in self.radical_terms:
                if radical_term.root == other.root \
                        and radical_term.content == other.content:
                    t = RadicalTerm(
                        radical_term.coefficient + other.coefficient,
                        radical_term.root,
                        radical_term.content,
                    )
                    if t.coefficient != ExactZero():
                        result_terms.append(t)
                    continue
                result_terms.append(radical_term)
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
        if isinstance(other, Numeric):
            return self * RadicalTerm.of(other)
        return other.__rmul__(self)

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

    def __truediv__(self, other):
        if isinstance(other, RadicalSum):
            if len(other.radical_terms) > 1:
                raise NotImplementedError
            return self / other.radical_terms[0]
        if isinstance(other, RadicalTerm):
            return sum(map(
                lambda x: x / other, self.radical_terms
            ), RadicalSum.of(0))

        return self / RadicalTerm.of(other)

    def __rtruediv__(self, other):
        if len(self.radical_terms) == 1:
            return RadicalSum(self.radical_terms[0].__rtruediv__(other))
        raise NotImplementedError

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
