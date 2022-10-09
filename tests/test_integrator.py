from decimal import Decimal
from unittest import TestCase

from advanced_functions.circle import Circle
from advanced_functions.elliptic import EllipticFunction
from calculus.integrator import Integrator, Mode, integrate_exact
from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction
from elementary_functions.simple import CharacteristicFunction, \
    SimpleFunction, Interval
from custom_numbers.computation import DecimalNumber


class TestIntegrator(TestCase):
    def test_integrate_linear(self):
        result = Integrator(
            DecimalNumber.of(0), Polynomial(0, 2).evaluate
        ).integrate(0, 2, 4)
        assert result.trap == 4
        assert result.min == 3
        assert result.max == 5

    def test_integrate_exact_power_func(self):
        assert integrate_exact(PowerFunction(2), -1, 2) == 3

    def test_integrate_exact_power_func_non_int(self):
        assert integrate_exact(PowerFunction(0.5, 1.5), 0, 4) == 8

    def test_integrate_exact_polynomial(self):
        # f(x) = -4  - x + 3x^2
        # F(x) = -4x - 1/2 x^2 + x^3
        # F(2) - F(-1) = -4.5
        assert integrate_exact(Polynomial(-4, -1, 3), -1, 2) == -4.5

    def test_integrate_exact_characteristic(self):
        func = CharacteristicFunction(Interval(-6, -2))\
                                + CharacteristicFunction(Interval(-1, 1))\
                                + CharacteristicFunction(Interval(2, 7))
        assert integrate_exact(func, -3, 4) == 5
        assert integrate_exact(func, -3, 0) == 2
        assert integrate_exact(func, 0, 8) == 6

    def test_integrate_exact_simple(self):
        func = SimpleFunction(
            CharacteristicFunction(Interval(-4, -1), 2),
            CharacteristicFunction(Interval(1, 3), -1),
            CharacteristicFunction(Interval(4, 7), 3),
        )
        assert integrate_exact(func, -3, 4) == 2
        assert integrate_exact(func, -2, 2) == 1
        assert integrate_exact(func, 0, 8) == 7

    def test_integrate_linear_increasing(self):
        result = Integrator(
            DecimalNumber.of(0),
            Polynomial(0, 2).evaluate, Mode.INCREASING
        ).integrate(0, 2, 4)
        assert result.trap == 4
        assert result.min == 3
        assert result.max == 5

    def test_integrate_linear_decreasing(self):
        result = Integrator(
            DecimalNumber.of(0),
            Polynomial(0, -2).evaluate, Mode.DECREASING
        ).integrate(0, 2, 4)
        assert result.trap == -4
        assert result.min == -5
        assert result.max == -3

    def test_integrate_parabola(self):
        integrator = Integrator(
            DecimalNumber.of(0),
            lambda x: 3 * x ** 2,
        )
        basic_result = integrator.integrate(-1, 1, 4)
        assert basic_result.trap == Decimal('2.25')
        assert basic_result.min == Decimal('0.75')
        assert basic_result.max == Decimal('3.75')

        messy_result = integrator.integrate(-1, 1, 5)
        assert messy_result.trap == Decimal('2.16')
        assert messy_result.min == Decimal('0.96')

    def test_calculate_circle_area(self):
        circle = Circle(0, 0, 2)
        integrator = Integrator(DecimalNumber.of(0), circle.evaluate, Mode.DECREASING)
        first_approximation = integrator.integrate(0, 2, 10)
        assert round(first_approximation.trap, 1) == Decimal('3.1')
        assert first_approximation.max > first_approximation.min
        assert first_approximation.max - first_approximation.min \
               < Decimal('0.5')

        second_approximation = integrator.integrate(0, 2, 100)
        assert round(second_approximation.trap, 2) == Decimal('3.14')
        assert second_approximation.max > second_approximation.min
        assert second_approximation.max - second_approximation.min \
               < Decimal('0.05')

    def test_calculate_circle_area_to_precision_one(self):
        integrator = Integrator(
            DecimalNumber.of(0),
            lambda x: 4 * (1 - x ** 2) ** Decimal('0.5'),
            Mode.DECREASING
        )
        assert integrator.integral_to_precision(0, 1, 1, 2)[0] \
               == Decimal('3.1')

    def test_calculate_elliptic_integrals(self):
        elliptic_function = EllipticFunction(2)

        elliptic_integrator_doubled = Integrator(
            DecimalNumber.of(0),
            elliptic_function.evaluate,
            Mode.DECREASING
        )
        assert elliptic_integrator_doubled.integral_to_precision(
            0, 1, precision=1, resolution=2,
            error_func_upper=elliptic_function.error_function
        )[0] == Decimal('4.8')
        # The true value of 2 * 2 * EllipticE(1 - 1 / 2^2) is
        # 4.8442241102738380992142515981959147059769591989433004125415581762
