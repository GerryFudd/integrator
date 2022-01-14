from unittest import TestCase

from elementary_functions.polynomials import Polynomial, Multipolynomial


class TestPolynomials(TestCase):
    def test_polynomial_addition(self):
        first = Polynomial(2, 1, 4)
        second = Polynomial(1, 5, 7)
        assert first.plus(second) == Polynomial(3, 6, 11)

    def test_polynomial_addition_summand_smaller(self):
        first = Polynomial(2, 1, 4, 3, 12)
        second = Polynomial(1, 5, 7)
        assert first.plus(second) == Polynomial(3, 6, 11, 3, 12)

    def test_polynomial_addition_summand_larger(self):
        first = Polynomial(2, 1, 4)
        second = Polynomial(1, 5, 7, 1, 3)
        assert first.plus(second) == Polynomial(3, 6, 11, 1, 3)

    def test_polynomial_addition_with_cancellation(self):
        first = Polynomial(2, 1, 4, -1, -3)
        second = Polynomial(1, 5, 7, 1, 3)
        assert first.plus(second) == Polynomial(3, 6, 11)

    def test_polynomial_multiplication(self):
        first = Polynomial(2, 1, 4)
        second = Polynomial(1, 5, 7)
        assert first.times(second) == Polynomial(2, 11, 23, 27, 28)


class TestMultipolynomial(TestCase):
    def test_multipolynomial_str(self):
        assert str(Multipolynomial(['a', 'b'], [[1, 0, -1], [0, 2], [-1]])) \
               == '1 + -b^2 + 2ab + -a^2'

    def test_multipolynomial_eq(self):
        assert Multipolynomial(['a', 'b'], [[1, 2], [3, 4]]) \
                == Multipolynomial(['b', 'a'], [[1, 3], [2, 4]])

    def test_multipolynomial_sum(self):
        first = Multipolynomial(['a', 'b'], [[1, 0, -1], [0, 2], [-1]])
        second = Multipolynomial(['a', 'b'], [[0, 1, 3], [1, -1], [2]])
        assert first.plus(second) == Multipolynomial(
            ['a', 'b'],
            [[1, 1, 2], [1, 1], [1]]
        )
