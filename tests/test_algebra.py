from algebra.equation import LinearEquation, PolynomialExpression, \
    QuadraticEquation
from algebra.inequality import LinearInequality, Condition
from general.interval import Interval


def test_solve_linear_equation():
    assert LinearEquation(
        PolynomialExpression(-3, 1),
        PolynomialExpression(4, 0)
    ).solve() == [7]


def test_solve_linear_inequality_lt():
    assert LinearInequality(
        PolynomialExpression(-3, 1),
        PolynomialExpression(4, 0),
        Condition.lt()
    ).solve() == [Interval.parse('(-inf, 7)')]


def test_solve_linear_inequality_le():
    assert LinearInequality(
        PolynomialExpression(-3, 1),
        PolynomialExpression(4, 0),
        Condition.le()
    ).solve() == [Interval.parse('(-inf, 7]')]


def test_solve_linear_inequality_gt():
    assert LinearInequality(
        PolynomialExpression(-3, 1),
        PolynomialExpression(4, 0),
        Condition.gt()
    ).solve() == [Interval.parse('(7, inf)')]


def test_solve_linear_inequality_ge():
    assert LinearInequality(
        PolynomialExpression(-3, 1),
        PolynomialExpression(4, 0),
        Condition.ge()
    ).solve() == [Interval.parse('[7, inf)')]


def test_solve_linear_with_division():
    assert LinearEquation(
        PolynomialExpression(-3, 4),
        PolynomialExpression(5, 0)
    ).solve() == [2]


def test_solve_linear_with_cancellation():
    assert LinearEquation(
        PolynomialExpression(-5, 5),
        PolynomialExpression(7, 2)
    ).solve() == [4]


def test_solve_quadratic_simple():
    assert QuadraticEquation(
        PolynomialExpression(-1, 0, 1),
        PolynomialExpression(0, 0, 0)
    ).solve() == [-1, 1]


def test_solve_quadratic():
    assert QuadraticEquation(
        PolynomialExpression(-7, 12, 2),
        PolynomialExpression(0, 0, 0)
    ).solve() == [-7, 1]


def test_solve_quadratic_with_cancellation():
    assert QuadraticEquation(
        PolynomialExpression(-5, 4, 15),
        PolynomialExpression(2, -8, 13)
    ).solve() == [-7, 1]


def test_solve_quadratic_reduces_linear():
    assert QuadraticEquation(
        PolynomialExpression(-5, 4, 15),
        PolynomialExpression(2, -10, 15)
    ).solve() == [0.5]
