from algebra.equation import LinearEquation, PolynomialExpression


def test_solve_linear():
    assert LinearEquation(
        PolynomialExpression(-3, 1),
        PolynomialExpression(4, 0)
    ).solve() == 7


def test_solve_linear_with_division():
    assert LinearEquation(
        PolynomialExpression(-3, 4),
        PolynomialExpression(5, 0)
    ).solve() == 2


def test_solve_linear_with_cancellation():
    assert LinearEquation(
        PolynomialExpression(-5, 5),
        PolynomialExpression(7, 2)
    ).solve() == 4
