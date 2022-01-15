from unittest import TestCase

from elementary_functions.multipolynomial import Multipolynomial


class TestMultipolynomial(TestCase):
    def test_multipolynomial_str(self):
        assert str(Multipolynomial(['a', 'b'], [[1, 0, -1], [0, 2], [-1]])) \
               == '1 + -b^2 + 2ab + -a^2'

    def test_multipolynomial_eq(self):
        # The polynomials represent alternate orderings
        # 1 + 2b + 3a + 4ab vs
        # 1 + 3a + 2b + 4ab
        assert Multipolynomial(['a', 'b'], [[1, 2], [3, 4]]) \
               == Multipolynomial(['b', 'a'], [[1, 3], [2, 4]])

    def test_multipolynomial_eq_three_vars(self):
        # Both polynomials represent
        # 1 + 2c + 3b + 4bc + 5a + 6ac + 7ab + 8abc
        # 1 + 2c + 5a + 6ac + 3b + 4bc + 7ab + 8abc
        assert Multipolynomial(['a', 'b', 'c'], [
            [[1, 2], [3, 4]], [[5, 6], [7, 8]]
        ]) == Multipolynomial(['b', 'a', 'c'], [
            [[1, 2], [5, 6]], [[3, 4], [7, 8]]
        ])

    def test_multipolynomial_sum(self):
        first = Multipolynomial(['a', 'b'], [[1, 0, -1], [0, 2], [-1]])
        second = Multipolynomial(['a', 'b'], [[0, 1, 3], [1, -1], [2]])
        assert first.plus(second) == Multipolynomial(
            ['a', 'b'],
            [[1, 1, 2], [1, 1], [1]]
        )
