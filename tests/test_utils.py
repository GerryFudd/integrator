from decimal import Decimal

from calculus.utils import get_local_extrema
from general.numbers import RationalNumber, Numeric


def test_get_local_extrema_for_line():
    result = get_local_extrema(lambda x: 2 * x, 1, 3)
    assert result == [1, 3]


def test_get_local_extrema_for_parabola():
    result = get_local_extrema(lambda x: x ** 2, -2, 2)
    assert result == [-2, 0, 2]


def test_get_local_extrema_for_cubic():
    result = get_local_extrema(lambda x: x ** 3 / 3 - x, -2, 2)
    assert result == [-2, -1, 1, 2]


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
           RationalNumber(1333, 100, False)


def test_from_dec():
    assert RationalNumber.from_dec(Decimal('13.33')) == \
           RationalNumber(1333, 100, False)


def test_abs():
    assert abs(RationalNumber(4, 13, False)) == RationalNumber(4, 13, False)
    assert abs(RationalNumber(-4, 13, False)) == RationalNumber(4, 13, False)
