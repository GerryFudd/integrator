from calculus.utils import get_local_extrema


def test_get_local_extrema_for_line():
    result = get_local_extrema(lambda x: 2 * x, 1, 3)
    assert result == [1, 3]


def test_get_local_extrema_for_parabola():
    result = get_local_extrema(lambda x: x ** 2, -2, 2)
    assert result == [-2, 0, 2]


def test_get_local_extrema_for_cubic():
    result = get_local_extrema(lambda x: x ** 3 / 3 - x, -2, 2)
    assert result == [-2, -1, 1, 2]
