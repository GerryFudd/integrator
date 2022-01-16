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

    def test_multipolynomial_sum_with_identity(self):
        # 1 + 2c + 3b + 4bc + 5a + 6ac + 7ab + 8abc
        multipoly = Multipolynomial(['a', 'b', 'c'], [
            [[1, 2], [3, 4]], [[5, 6], [7, 8]]
        ])
        ident = Multipolynomial([], [])
        assert multipoly.plus(ident) == multipoly
        assert ident.plus(multipoly) == multipoly
        assert ident.plus(ident) == ident

    def test_multipolynomial_sum_with_inverse(self):
        multipoly = Multipolynomial(['a', 'b', 'c'], [
            [[1, 2], [3, 4]], [[5, 6], [7, 8]]
        ])
        inverse = Multipolynomial(['a', 'b', 'c'], [
            [[-1, -2], [-3, -4]], [[-5, -6], [-7, -8]]
        ])
        ident = Multipolynomial([], [])
        assert multipoly.plus(inverse) == ident
        assert inverse.plus(multipoly) == ident

    def test_multipolynomial_sum_different_order(self):
        first = Multipolynomial(['a', 'b'], [[1, 0, -1], [0, 2], [-1]])
        second = Multipolynomial(['b', 'a'], [[0, 1, 2], [1, -1], [3]])
        assert first.plus(second) == Multipolynomial(
            ['a', 'b'],
            [[1, 1, 2], [1, 1], [1]]
        )

    def test_multipolynomial_sum_three_variables_different_order(self):
        # 1 + 2c + 3c^2 + 4b + 5bc + 6bc^2 + 7b^2 + 8b^2c + 9b^2c^2 +
        # 10a + 11ac + 12ac^2 + 13ab + 14abc + 15abc^2 + 16ab^2 + 17ab^2c +
        # 18ab^2c^2
        # 19a^2 + 20a^2c + 21a^2c^2 + 22a^2b + 23a^2bc + 24a^2bc^2 +
        # 25a^2b^2 + 26a^2b^2c + 27a^2b^2c^2
        first = Multipolynomial(['a', 'b', 'c'], [
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
            [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
        ])
        # 1 + 2a + 3a^2 + 4c + 5ca + 6ca^2 + 7c^2 + 8c^2a + 9c^2a^2 +
        # 10b + 11ba + 12ba^2 + 13bc + 14bca + 15bca^2 + 16bc^2 + 17bc^2a +
        # 18bc^2a^2
        # 19b^2 + 20b^2a + 21b^2a^2 + 22b^2c + 23b^2ca + 24b^2ca^2 +
        # 25b^2c^2 + 26b^2c^2a + 27b^2c^2a^2
        second = Multipolynomial(['b', 'c', 'a'], [
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
            [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
        ])
        # 2 + 6c + 10c^2 + 14b + 18bc + 22bc^2 + 26b^2 + 30b^2c + 34b^2c^2 +
        # 12a + 16ac + 20ac^2 + 24ab + 28abc + 32abc^2 + 36ab^2 + 40ab^2c +
        # 44ab^2c^2
        # 22a^2 + 26a^2c + 30a^2c^2 + 34a^2b + 38a^2bc + 42a^2bc^2 +
        # 46a^2b^2 + 50a^2b^2c + 54a^2b^2c^2
        assert first.plus(second) == Multipolynomial(
            ['a', 'b', 'c'],
            [
                [[2, 6, 10], [14, 18, 22], [26, 30, 34]],
                [[12, 16, 20], [24, 28, 32], [36, 40, 44]],
                [[22, 26, 30], [34, 38, 42], [46, 50, 54]]
            ]
        )

    def test_multipolynomial_sum_different_variables(self):
        assert Multipolynomial(['a'], [1, 2])\
            .plus(Multipolynomial(['b'], [3, 4])) == Multipolynomial(
            ['a', 'b'], [[4, 4], [2]]
        )
