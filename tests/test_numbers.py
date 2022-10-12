from decimal import Decimal

from custom_numbers.exact.factory import to_exact
from custom_numbers.exact.rational_number import RationalNumber
from custom_numbers.radicals.radical_sum import RadicalSum
from custom_numbers.radicals.radical_term import RadicalTerm
from custom_numbers.utils import newton_int_sqrt
from custom_numbers.types import Numeric


def test_rational_number_from_int():
    assert str(RationalNumber(7)) == '7'


def test_rational_number_with_denom():
    assert str(RationalNumber(7, 4)) == '1.75'


def test_rational_number_with_neg_denom():
    assert RationalNumber(7, -4) == RationalNumber(-7, 4)


def test_rational_number_with_0_num():
    assert RationalNumber(0, -4) == RationalNumber(0)


def test_rational_number_sum():
    assert RationalNumber(3, 4) + RationalNumber(5, 6) == RationalNumber(19, 12)


def test_rational_number_sum_int():
    assert RationalNumber(2, 7) + 2 == RationalNumber(16, 7)


def test_rational_number_sum_float():
    assert RationalNumber(3, 8) + 0.625 == 1


def test_rational_number_sum_decimal():
    assert RationalNumber(3, 8) + Decimal('0.625') == 1


def test_rational_number_prod_int():
    assert RationalNumber(5, 6) * 2 == RationalNumber(5, 3)


def test_rational_number_prod_rational():
    assert RationalNumber(5, 6) * RationalNumber(2, 7) == RationalNumber(5, 21)


def test_rational_number_sub():
    assert RationalNumber(3, 4) - RationalNumber(5, 6) == RationalNumber(-1, 12)


def test_rational_number_sub_int():
    assert RationalNumber(3, 4) - 2 == RationalNumber(-5, 4)


def test_rational_number_is_numeric():
    assert isinstance(RationalNumber(7), Numeric)


def test_eq_int():
    assert RationalNumber(7) == 7


def test_eq_float():
    assert RationalNumber(7, 8) == 0.875


def test_eq_neg_float():
    assert RationalNumber(-9, 2) == -4.5


def test_neq_int():
    assert RationalNumber(7) != 8


def test_neq_float():
    assert RationalNumber(7, 8) != 0.87


def test_lt():
    assert RationalNumber(7) < RationalNumber(8)


def test_lt_float():
    assert RationalNumber(7, 8) < 0.88


def test_lt_decimal():
    assert RationalNumber(7, 8) < Decimal('0.88')


def test_from_dec_str():
    assert RationalNumber.from_dec_str('13.33') == \
           RationalNumber(1333, 100)


def test_from_dec():
    assert RationalNumber.from_dec(Decimal('13.33')) == \
           RationalNumber(1333, 100)


def test_abs():
    assert abs(RationalNumber(4, 13)) == RationalNumber(4, 13)
    assert abs(RationalNumber(-4, 13)) == RationalNumber(4, 13)


def test_int_sqrt_perfect_squares():
    assert newton_int_sqrt(0) == 0
    assert newton_int_sqrt(1) == 1
    assert newton_int_sqrt(4) == 2
    assert newton_int_sqrt(9) == 3
    assert newton_int_sqrt(16) == 4


def test_int_sqrt_closest_int():
    assert newton_int_sqrt(2) == 1
    assert newton_int_sqrt(3) in (1, 2)
    assert newton_int_sqrt(5) in (2, 3)
    assert newton_int_sqrt(6) in (2, 3)
    assert newton_int_sqrt(7) in (2, 3)
    assert newton_int_sqrt(8) in (2, 3)
    assert newton_int_sqrt(10) in (3, 4)
    assert newton_int_sqrt(11) in (3, 4)
    assert newton_int_sqrt(12) in (3, 4)
    assert newton_int_sqrt(13) in (3, 4)
    assert newton_int_sqrt(14) in (3, 4)
    assert newton_int_sqrt(15) in (3, 4)
    assert newton_int_sqrt(17) in (4, 5)
    assert newton_int_sqrt(18) in (4, 5)
    assert newton_int_sqrt(19) in (4, 5)
    assert newton_int_sqrt(20) in (4, 5)
    assert newton_int_sqrt(21) in (4, 5)
    assert newton_int_sqrt(22) in (4, 5)
    assert newton_int_sqrt(23) in (4, 5)
    assert newton_int_sqrt(24) in (4, 5)


# def test_newton_sqrt_exact():
#     assert RationalNumber(0, 1) ** 0.5 == 0
#     assert RationalNumber(1, 1) ** 0.5 == 1
#     assert RationalNumber(1, 4) ** 0.5 == 0.5
#     assert RationalNumber(4, 9) ** 0.5 == RationalNumber(2, 3)
#     assert RationalNumber(9, 4) ** 0.5 == 1.5
#     assert RationalNumber(9, 16) ** 0.5 == 0.75
#     assert RationalNumber(25, 16) ** 0.5 == 1.25


# def test_sqrt_approx():
#     tolerance = 12
#     assert round(RationalNumber(2, 1) ** 0.5, tolerance) == \
#            round(Decimal(2) ** Decimal('0.5'), tolerance)
#     assert round(RationalNumber(3, 2) ** 0.5, tolerance) == \
#            round(Decimal('1.5') ** Decimal('0.5'), tolerance)

def test_radical_term_constructor():
    assert RadicalTerm(RationalNumber(5)) == RadicalTerm(
        RationalNumber(5),
        1, RationalNumber(1)
    )
    assert RadicalTerm(RationalNumber(2), 1, RationalNumber(3)) == RadicalTerm(
        RationalNumber(6),
    )
    assert RadicalTerm(RationalNumber(2), 3, RationalNumber(-3)) == RadicalTerm(
        RationalNumber(-2),
        3, RationalNumber(3)
    )
    assert RadicalTerm(RationalNumber(5), 17, RationalNumber(0)) == \
           RadicalTerm(RationalNumber(0))


def test_radical_term_sum():
    a = RadicalTerm.reduced(7, 2, RationalNumber(5))
    b = RadicalTerm.reduced(4, 2, RationalNumber(5))
    assert a + b == RadicalTerm.reduced(11, 2, RationalNumber(5))


def test_radical_term_prod():
    a = RadicalTerm(RationalNumber(7), 6, RationalNumber(3))
    b = RadicalTerm(RationalNumber(4), 10, RationalNumber(4))
    assert a * b == RadicalTerm.reduced(28, 30, RationalNumber(3 ** 5 * 4 ** 3))


def test_radical_term_eq_rational():
    assert RadicalTerm(RationalNumber(3, 7), 2, RationalNumber(4)) != \
           RationalNumber(6, 7)
    assert RadicalTerm(RationalNumber(6, 7)) == RationalNumber(6, 7)


def test_radical_term_reduce_extract_exact_root_factor():
    assert RadicalTerm.reduced(RationalNumber(3, 7), 2, RationalNumber(4)) == \
           RationalNumber(6, 7)
    assert RadicalTerm.reduced(RationalNumber(3, 7), 2, RationalNumber(8, 9)) \
           == RadicalTerm(RationalNumber(6, 21), 2, RationalNumber(2))
    assert RadicalTerm.reduced(1, 2, RationalNumber(
        23**2*29**3*101, 24
    )) == RadicalTerm(
        RationalNumber(23 * 29, 2), 2, RationalNumber(29 * 101, 6)
    )


def test_radical_term_reduce_reduce_root_by_factor():
    assert RadicalTerm.reduced(RationalNumber(1), 6, RationalNumber(25)) == \
           RadicalTerm(RationalNumber(1), 3, RationalNumber(5))
    assert RadicalTerm.reduced(RationalNumber(1), 6, RationalNumber(125)) == \
           RadicalTerm(RationalNumber(1), 2, RationalNumber(5))


def test_radical_term_reduce_extract_root_factor_and_reduce_root():
    assert RadicalTerm.reduced(RationalNumber(1), 6, RationalNumber(2304)) == \
        RadicalTerm(RationalNumber(2), 3, RationalNumber(6))


def test_radical_term_pow():
    a = RadicalTerm(RationalNumber(7, 5), 3, RationalNumber(25, 49))
    assert a ** 3 == RationalNumber(7, 5)
    b = RadicalTerm(RationalNumber(10, 17), 2, RationalNumber(17 * 61, 65))
    assert b ** 3 == RadicalTerm(
        RationalNumber(2**3*5**2*61, 13*17**2), 2, RationalNumber(17*61, 65)
    )


def test_exact_constructor():
    assert isinstance(to_exact(1), RadicalSum)
    assert isinstance(to_exact(1.25), RadicalSum)
    assert isinstance(RadicalSum(
        RadicalTerm.reduced(3, 2, RationalNumber(5)),
        RadicalTerm.of(7),
    ), RadicalSum)


def test_radical_sum_multiplication():
    a = RadicalSum(
        RadicalTerm(RationalNumber(12), 2, RationalNumber(5)),
        RadicalTerm(RationalNumber(4), 2, RationalNumber(7)),
    )
    b = RadicalSum(
        RadicalTerm(RationalNumber(12), 2, RationalNumber(5)),
        RadicalTerm(RationalNumber(-4), 2, RationalNumber(7)),
    )
    assert a * b == RadicalSum.of(144 * 5 - 16 * 7)


def test_radical_sum_limited_flip_one_term():
    one_term_sum = RadicalSum(
        RadicalTerm(RationalNumber(2, 3), 2, RationalNumber(5, 3))
    )
    assert 1 / one_term_sum == RadicalSum(
        RadicalTerm(RationalNumber(3, 2), 2, RationalNumber(3, 5))
    )


def test_radical_sum_limited_flip_two_terms():
    two_term_sum = RadicalSum(
        RadicalTerm(RationalNumber(2), 2, RationalNumber(5)),
        RadicalTerm(RationalNumber(3), 3, RationalNumber(4))
    )
    assert 1 / two_term_sum == RadicalSum(
        RadicalTerm(RationalNumber(-50, 229), 2, RationalNumber(5)),
        RadicalTerm(RationalNumber(75, 229), 3, RationalNumber(4)),
        RadicalTerm(RationalNumber(-45, 229), 6, RationalNumber(500)),
        RadicalTerm(RationalNumber(135, 229)),
        RadicalTerm(RationalNumber(-81, 458), 6, RationalNumber(2000)),
        RadicalTerm(RationalNumber(243, 458), 3, RationalNumber(2)),
    )
