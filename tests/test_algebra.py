from algebra.equation import LinearEquation, LinearExpression


def test_solve_linear():
    assert LinearEquation(
        LinearExpression(1, -3),
        LinearExpression(0, 4)
    ).solve() == 7


def test_solve_linear_with_division():
    assert LinearEquation(
        LinearExpression(4, -3),
        LinearExpression(0, 5)
    ).solve() == 2


def test_solve_linear_with_cancellation():
    assert LinearEquation(
        LinearExpression(5, -5),
        LinearExpression(2, 7)
    ).solve() == 4
