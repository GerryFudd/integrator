from unittest import TestCase

from elementary_functions.polynomial import Polynomial


class TestPolynomial(TestCase):
    def test_polynomial_addition(self):
        first = Polynomial(2, 1, 4)
        second = Polynomial(1, 5, 7)
        assert first + second == Polynomial(3, 6, 11)

    def test_polynomial_addition_summand_smaller(self):
        first = Polynomial(2, 1, 4, 3, 12)
        second = Polynomial(1, 5, 7)
        assert first + second == Polynomial(3, 6, 11, 3, 12)

    def test_polynomial_addition_summand_larger(self):
        first = Polynomial(2, 1, 4)
        second = Polynomial(1, 5, 7, 1, 3)
        assert first + second == Polynomial(3, 6, 11, 1, 3)

    def test_polynomial_addition_with_cancellation(self):
        first = Polynomial(2, 1, 4, -1, -3)
        second = Polynomial(1, 5, 7, 1, 3)
        assert first + second == Polynomial(3, 6, 11)

    def test_polynomial_multiplication(self):
        first = Polynomial(2, 1, 4)
        second = Polynomial(1, 5, 7)
        assert first * second == Polynomial(2, 11, 23, 27, 28)



