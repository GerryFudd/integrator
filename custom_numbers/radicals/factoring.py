from __future__ import annotations

from typing import Dict, List


class PrimeFactorization:
    def __init__(self, factors: Dict[int, int]):
        self.factors = factors

    def __iter__(self):
        return self.factors.items().__iter__()

    def exact_root(self, root: int) -> tuple[int, int]:
        if root < 1:
            return NotImplemented
        result = 1
        remainder = 1
        for prime, multiplicity in self:
            res_pow, rem_pow = divmod(multiplicity, root)
            result *= prime ** res_pow
            remainder *= prime ** rem_pow
        return result, remainder

    def reduce(self, root: int) -> tuple[PrimeFactorization, int]:
        if root < 1:
            return NotImplemented
        new_factors = {}

        for prime, multiplicity in self:
            res_pow, rem_pow = divmod(multiplicity, root)
            if rem_pow != 0:
                return self, root
            new_factors[prime] = res_pow
        return PrimeFactorization(new_factors), 1


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
