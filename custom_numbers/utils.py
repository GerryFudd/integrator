from __future__ import annotations


def minimum(a, b):
    if a <= b:
        return a
    return b


def maximum(a, b):
    if a >= b:
        return a
    return b


def gcd(a: int, b: int):
    if a < 0 or b < 0:
        return gcd(abs(a), abs(b))
    if a == 0:
        return b
    if b == 0:
        return a

    n = maximum(a, b)
    m = minimum(a, b)

    return gcd(m, n % m)


def newton_int_sqrt(x: int) -> int:
    if x == 0:
        return 0
    if x < 0:
        raise NotImplementedError
    candidate = x

    while True:
        next_candidate = (candidate + x // candidate) // 2
        if abs(candidate - next_candidate) <= 1:
            return next_candidate
        candidate = next_candidate
