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

    def test_multipolynomial_sum_with_cancellation(self):
        first = Multipolynomial(['a', 'b'], [[3, 7, -14], [0, 3], [-2]])
        second = Multipolynomial(['a', 'b'], [[5, -7, 14], [1, -3], [2]])
        assert first.plus(second) == Multipolynomial(
            ['a'],
            [8, 1]
        )

    def test_multipolynomial_sum_with_cancellation_of_first_variable(self):
        first = Multipolynomial(['a', 'b'], [[3, 0, -2], [7, 3], [-14]])
        second = Multipolynomial(['a', 'b'], [[5, 1, 2], [-7, -3], [14]])
        assert first.plus(second) == Multipolynomial(
            ['b'],
            [8, 1]
        )

    def test_multipolynomial_sum_with_cancellation_of_middle_variable(self):
        # 1 + 2c + 3b + 4bc + 5a + 6ac + 7ab + 8abc
        first = Multipolynomial(['a', 'b', 'c'], [
            [[1, 2], [3, 4]], [[5, 6], [7, 8]]
        ])
        # 2 + 3c + -3b + -4bc + 5a + 7ac + -7ab + -8abc
        second = Multipolynomial(['a', 'b', 'c'], [
            [[2, 3], [-3, -4]], [[5, 7], [-7, -8]]
        ])
        # 3 + 5c + 10a + 13ac
        assert first.plus(second) == Multipolynomial(
            ['a', 'c'],
            [[3, 5], [10, 13]]
        )

    def test_multipolynomial_sum_different_order(self):
        first = Multipolynomial(['a', 'b'], [[1, 0, -1], [0, 2], [-1]])
        second = Multipolynomial(['b', 'a'], [[0, 1, 2], [1, -1], [3]])
        assert first.plus(second) == Multipolynomial(
            ['a', 'b'],
            [[1, 1, 2], [1, 1], [1]]
        )
