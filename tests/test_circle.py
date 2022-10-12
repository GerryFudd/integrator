from advanced_functions.circle import Circle
from custom_numbers.computation import DecimalNumber
from custom_numbers.exact.factory import to_exact
from custom_numbers.exact.types import ExactNumber


def test_unit_circle():
    circ = Circle(0, 0, 1)
    for n in range(201):
        exact_val: ExactNumber = (to_exact(n) - 100) / 100
        actual: ExactNumber = circ.evaluate(exact_val)
        print(f'actual: {actual}')
        decimal_val = (DecimalNumber.of(n) - 100) / 100
        expected = (1 - decimal_val ** 2) ** 0.5
        print(f'expected: {expected}')
        assert round(actual.to_decimal(), 12) == round(expected, 12)
