from advanced_functions.circle import Circle
from custom_numbers.computation import Number
from custom_numbers.exact import ExactNumber


def test_unit_circle():
    circ = Circle(0, 0, 1)
    for n in range(201):
        exact_val: ExactNumber = (ExactNumber.of(n) - 100) / 100
        actual: ExactNumber = circ.evaluate(exact_val)
        print(f'actual: {actual}')
        decimal_val = (Number.of(n) - 100) / 100
        expected = (1 - decimal_val ** 2) ** 0.5
        print(f'expected: {expected}')
        assert round(actual.to_number(), 12) == round(expected, 12)
