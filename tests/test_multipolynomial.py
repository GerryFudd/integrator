from unittest import TestCase

from elementary_functions.multipolynomial import Multipolynomial


class TestMultipolynomial(TestCase):
    def test_multipolynomial_str(self):
        assert str(Multipolynomial(['a', 'b'], [[1, 0, -1], [0, 2], [-1]])) \
               == '1 + -b^2 + 2ab + -a^2'
        assert str(Multipolynomial(['a', 'b'], [[-1, 0, -1], [0, 2], [-1]])) \
               == '-1 + -b^2 + 2ab + -a^2'

    def test_multipolynomial_eq(self):
        # The polynomials represent alternate orderings
        # 1 + 2b + 3a + 4ab vs
        # 1 + 3a + 2b + 4ab
        assert Multipolynomial(['b', 'a'], [[1, 3], [2, 4]]).re_map_indices() \
               == Multipolynomial(['a', 'b'], [[1, 2], [3, 4]])

    def test_multipolynomial_eq_three_vars(self):
        # Both polynomials represent
        # 1 + 2c + 3b + 4bc + 5a + 6ac + 7ab + 8abc
        # 1 + 2c + 5a + 6ac + 3b + 4bc + 7ab + 8abc
        assert Multipolynomial(['b', 'c', 'a'], [
            [[1, 5], [2, 6]], [[3, 7], [4, 8]]
        ]).re_map_indices() == Multipolynomial(['a', 'b', 'c'], [
            [[1, 2], [3, 4]], [[5, 6], [7, 8]]
        ])

    def test_multipolynomial_reduce(self):
        assert Multipolynomial(
            ['a', 'b', 'c'], [
                [[0, 0], [0, 0]], [[10, 13], [0, 0]]
            ]
        )._reduce() == Multipolynomial(
            ['a', 'c'], [[], [10, 13]]
        )


class TestMultipolynomialSum(TestCase):
    def test_multipolynomial_sum(self):
        first = Multipolynomial(['a', 'b'], [[1, 0, -1], [0, 2], [-1]])
        second = Multipolynomial(['a', 'b'], [[0, 1, 3], [1, -1], [2]])
        assert first + second == Multipolynomial(
            ['a', 'b'],
            [[1, 1, 2], [1, 1], [1]]
        )

    def test_multipolynomial_sum_with_cancellation(self):
        first = Multipolynomial(['a', 'b'], [[3, 7, -14], [0, 3], [-2]])
        second = Multipolynomial(['a', 'b'], [[5, -7, 14], [1, -3], [2]])
        assert first + second == Multipolynomial(
            ['a'],
            [8, 1]
        )

    def test_multipolynomial_sum_with_cancellation_of_first_variable(self):
        first = Multipolynomial(['a', 'b'], [[3, 0, -2], [7, 3], [-14]])
        second = Multipolynomial(['a', 'b'], [[5, 1, 2], [-7, -3], [14]])
        assert first + second == Multipolynomial(
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
        assert first + second == Multipolynomial(
            ['a', 'c'],
            [[3, 5], [10, 13]]
        )

    def test_multipolynomial_sum_with_collapsed_list(self):
        # 1 + 2c + 3b + 4bc + 5a + 6ac + 7ab + 8abc
        first = Multipolynomial(['a', 'b', 'c'], [
            [[1, 2], [3, 4]], [[5, 6], [7, 8]]
        ])
        # -1 - 2c + -3b + -4bc + 5a + 7ac + -7ab + -8abc
        second = Multipolynomial(['a', 'b', 'c'], [
            [[-1, -2], [-3, -4]], [[5, 7], [-7, -8]]
        ])
        # 3 + 5c + 10a + 13ac
        assert first + second == Multipolynomial(
            ['a', 'c'],
            [[], [10, 13]]
        )

    def test_multipolynomial_sum_with_identity(self):
        # 1 + 2c + 3b + 4bc + 5a + 6ac + 7ab + 8abc
        multipoly = Multipolynomial(['a', 'b', 'c'], [
            [[1, 2], [3, 4]], [[5, 6], [7, 8]]
        ])
        ident = Multipolynomial.zero()
        assert multipoly + ident == multipoly
        assert ident + multipoly == multipoly
        assert ident + ident == ident

    def test_multipolynomial_sum_with_inverse(self):
        x = Multipolynomial(['a', 'b', 'c'], [
            [[1, 2], [3, 4]], [[5, 6], [7, 8]]
        ])
        inverse = Multipolynomial(['a', 'b', 'c'], [
            [[-1, -2], [-3, -4]], [[-5, -6], [-7, -8]]
        ])
        ident = Multipolynomial.zero()
        assert x + inverse == ident
        assert inverse + x == ident

    def test_multipolynomial_sum_different_order(self):
        first = Multipolynomial(['a', 'b'], [[1, 0, -1], [0, 2], [-1]])
        second = Multipolynomial(['b', 'a'], [[0, 1, 2], [1, -1], [3]])
        assert first + second == Multipolynomial(
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
        assert first + second == Multipolynomial(
            ['a', 'b', 'c'],
            [
                [[2, 6, 10], [14, 18, 22], [26, 30, 34]],
                [[12, 16, 20], [24, 28, 32], [36, 40, 44]],
                [[22, 26, 30], [34, 38, 42], [46, 50, 54]]
            ]
        )

    def test_multipolynomial_sum_different_variables(self):
        assert Multipolynomial(['a'], [1, 2]) \
                   + Multipolynomial(['b'], [3, 4]) == Multipolynomial(
            ['a', 'b'], [[4, 4], [2]]
        )


class TestMultipolynomialProduct(TestCase):
    def test_multipolynomial_product(self):
        # 1 + -b^2 + 2ab + -a^2
        first = Multipolynomial(['a', 'b'], [[1, 0, -1], [0, 2], [-1]])
        # b + 3b^2 + a + -ab + 2a^2
        second = Multipolynomial(['a', 'b'], [[0, 1, 3], [1, -1], [2]])
        # -3a^2b^2 + -2a^2b^2 + -2a^2b^2

        # b + 3b^2 + -b^3 + -3b^4 +
        # a + -ab + ab^2 + 7ab^3 +
        # 2a^2 + a^2b + -7a^2b^2 +
        # -a^3 + 5a^3b
        # -2a^4
        assert first * second == Multipolynomial(
            ['a', 'b'],
            [
                [0, 1, 3, -1, -3], [1, -1, 1, 7], [2, 1, -7],
                [-1, 5], [-2]
            ]
        )

    def test_multipolynomial_product_handles_identity(self):
        first = Multipolynomial(['a', 'b'], [[1, 2, 3], [4, 5], [6]])
        # assert first * Multipolynomial.one() == first
        assert Multipolynomial.one() * first == first
        assert Multipolynomial.one() * Multipolynomial.one() == \
               Multipolynomial.one()

    def test_multipolynomial_product_handles_zero(self):
        first = Multipolynomial(['a', 'b'], [[1, 2, 3], [4, 5], [6]])
        assert first * Multipolynomial.zero() == Multipolynomial.zero()
        assert Multipolynomial.zero() * first == Multipolynomial.zero()
        assert Multipolynomial.zero() * Multipolynomial.zero() == \
               Multipolynomial.zero()

    def test_multipolynomial_product_handles_cancellation(self):
        first = Multipolynomial(['a', 'b'], [[0, 1], [1]])
        second = Multipolynomial(['a', 'b'], [[0, -1], [1]])
        assert first * second == Multipolynomial(
            ['a', 'b'], [[0, 0, -1], [], [1]]
        )


class TestMultipolynomialPower(TestCase):
    def test_multipolynomial_power(self):
        assert Multipolynomial(['a', 'b'], [[0, 1], [1]]) ** 2 == \
               Multipolynomial(['a', 'b'], [[0, 0, 1], [0, 2], [1]])

    def test_multipolynomial_power_handles_one(self):
        assert Multipolynomial(['a', 'b'], [[0, 1], [1]]) ** 1 == \
               Multipolynomial(['a', 'b'], [[0, 1], [1]])

    def test_multipolynomial_power_handles_zero(self):
        assert Multipolynomial(['a', 'b'], [[0, 1], [1]]) ** 0 == \
               Multipolynomial.one()

    def test_multipolynomial_power_larger(self):
        assert Multipolynomial(['a', 'b'], [[0, 1], [1]]) ** 5 == \
               Multipolynomial(['a', 'b'], [
                   [0, 0, 0, 0, 0, 1],
                   [0, 0, 0, 0, 5],
                   [0, 0, 0, 10],
                   [0, 0, 10],
                   [0, 5],
                   [1]
               ])

    def test_multipolynomial_power_more_cross(self):
        assert Multipolynomial(
            ['a', 'b', 'c'], [[[1, 3], [5, 7]], [[11, 13], [17, 19]]]
        ) ** 2 \
               == Multipolynomial(
            ['a', 'b', 'c'], [
                [[1, 6, 9], [10, 44, 42], [25, 70, 49]],
                [[22, 92, 78], [144, 424, 296], [170, 428, 266]],
                [[121, 286, 169], [374, 860, 494], [289, 646, 361]]
            ]
        )

    def test_wtf(self):
        a = Multipolynomial.named('a')
        b = Multipolynomial.named('b')
        c = Multipolynomial.named('c')

        x = (a + b) ** 2 - 2 * c

        assert x == Multipolynomial(
            ['a', 'b', 'c'],
            [
                [[0, -2], [], [1]],
                [[], [2]],
                [[1]]
            ]
        )

    def test_multipolynomial_reduce(self):
        # a + b
        x = Multipolynomial(
            ['a', 'b'],
            [[0, 1], [1, 0]]
        )
        # c
        c = Multipolynomial(['c'], [0, 1])

        # ((a + b)^2 - 2(a + b)c + c^2)
        # a^2 + b^2 + c^2 + 2ab - 2ac - 2bc
        assert (x ** 2 - 2 * x * c + c ** 2) == Multipolynomial(
            ['a', 'b', 'c'], [
                [[0, 0, 1], [0, -2], [1]],
                [[0, -2], [2]],
                [[1]]
            ]
        )

    def test_big_product(self):
        x = Multipolynomial(['x'], [0, 1])
        y = Multipolynomial(['y'], [0, 1])
        z = Multipolynomial(['z'], [0, 1])

        t = (x + y) ** 2 - (x + y) * z + z**2

        u = x ** 3 - 2 * y ** 3 + z ** 3
        v = 2 * x ** 3 - y ** 3 - z ** 3
        w = u ** 2 * x ** 2 - u * v * x * y + v ** 2 * y ** 2

        result = t * (x - y) * w
        # print(result)
        # -y^3z^8+y^4z^7-y^5z^6-2y^6z^5+2y^7z^4-2y^8z^3-y^9z^2+y^(10)z-y^(11) 
        # xy^3z^7-2xy^4z^6+3xy^5z^5-xy^6z^4-xy^7z^3+3xy^8z^2-2xy^9z+xy^(10) 
        # -x^2y^3z^6+3x^2y^4z^5-6x^2y^5z^4+7x^2y^6z^3-6x^2y^7z^2+3x^2y^8z-x^2y^9 
        # x^3z^8-x^3yz^7+x^3y^2z^6-3x^3y^4z^4+9x^3y^5z^3+8x^3y^6z^2-2x^3y^7z-x^3y^8 
        # -x^4z^7+2x^4yz^6-3x^4y^2z^5+3x^4y^3z^4-9x^4y^5z^2+x^4y^6z+x^4y^7 
        # +x^5z^6-3x^5yz^5+6x^5y^2z^4-9x^5y^3z^3+9x^5y^4z^2-x^5y^6 
        # +2x^6z^5+x^6yz^4-7x^6y^2z^3-8x^6y^3z^2-x^6y^4z+x^6y^5 
        # -2x^7z^4+x^7yz^3+6x^7y^2z^2+2x^7y^3z-x^7y^4 
        # +2x^8z^3-3x^8yz^2-3x^8y^2z+x^8y^3 
        # +x^9z^2+2x^9yz+x^9y^2 
        # -x^(10)z-x^(10)y 
        # +x^(11)
        #
        # print((x + y + z) * result)
        # -y^3z^9 + -3y^6z^6 + -3y^9z^3 + -y^(12) 
        # + x^3z^9 + 24x^3y^6z^3 + -2x^3y^9 
        # + 3x^6z^6 + -24x^6y^3z^3 
        # + 3x^9z^3 + 2x^9y^3 
        # + x^(12)

        assert result == Multipolynomial(
            ['x', 'y', 'z'],
            [
                [
                    [],
                    [],
                    [],
                    [0, 0, 0, 0, 0, 0, 0, 0, -1],
                    [0, 0, 0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0, -1],
                    [0, 0, 0, 0, 0, -2],
                    [0, 0, 0, 0, 2],
                    [0, 0, 0, -2],
                    [0, 0, -1],
                    [0, 1],
                    [-1]
                ],
                [
                    [],
                    [],
                    [],
                    [0, 0, 0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0, -2],
                    [0, 0, 0, 0, 0, 3],
                    [0, 0, 0, 0, -1],
                    [0, 0, 0, -1],
                    [0, 0, 3],
                    [0, -2],
                    [1]
                ],
                [
                    [],
                    [],
                    [],
                    [0, 0, 0, 0, 0, 0, -1],
                    [0, 0, 0, 0, 0, 3],
                    [0, 0, 0, 0, -6],
                    [0, 0, 0, 7],
                    [0, 0, -6],
                    [0, 3],
                    [-1]
                ],
                [
                    [0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0, 0, -1],
                    [0, 0, 0, 0, 0, 0, 1],
                    [],
                    [0, 0, 0, 0, -3],
                    [0, 0, 0, 9],
                    [0, 0, 8],
                    [0, -2],
                    [-1]
                ],
                [
                    [0, 0, 0, 0, 0, 0, 0, -1],
                    [0, 0, 0, 0, 0, 0, 2],
                    [0, 0, 0, 0, 0, -3],
                    [0, 0, 0, 0, 3],
                    [],
                    [0, 0, -9],
                    [0, 1],
                    [1]
                ],
                [
                    [0, 0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, -3],
                    [0, 0, 0, 0, 6],
                    [0, 0, 0, -9],
                    [0, 0, 9],
                    [],
                    [-1]
                ],
                [
                    [0, 0, 0, 0, 0, 2],
                    [0, 0, 0, 0, 1],
                    [0, 0, 0, -7],
                    [0, 0, -8],
                    [0, -1],
                    [1]
                ],
                [
                    [0, 0, 0, 0, -2],
                    [0, 0, 0, 1],
                    [0, 0, 6],
                    [0, 2],
                    [-1]
                ],
                [
                    [0, 0, 0, 2],
                    [0, 0, -3],
                    [0, -3],
                    [1]
                ],
                [
                    [0, 0, 1],
                    [0, 2],
                    [1]
                ],
                [
                    [0, -1],
                    [-1]
                ],
                [
                    [1]
                ]
            ],
        )

    def test_multipolynomial_remap(self):
        # a + b
        x = Multipolynomial(
            ['a', 'b'],
            [[0, 1], [1, 0]]
        )
        # c
        c2 = Multipolynomial(
            ['c'],
            [0, 0, 1]
        )

        # ((a + b)^2 - 2(a + b)c + c^2)
        # a^2 + b^2 + c^2 + 2ab - 2ac - 2bc
        z = x + c2
        print(z)
        assert z == Multipolynomial(
            ['a', 'b', 'c'], [
                [[0, 0, 1], [1]],
                [[1]]
            ]
        )
