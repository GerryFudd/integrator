from decimal import Decimal
from unittest import TestCase

from calculus.integrator import Integrator, Mode


class TestIntegrator(TestCase):
    def test_integrate_linear(self):
        result = Integrator(lambda x: 2 * x).integrate(0, 2, 4)
        assert result.trap == 4
        assert result.min == 3
        assert result.max == 5

    def test_integrate_linear_increasing(self):
        result = Integrator(lambda x: 2 * x, Mode.INCREASING).integrate(0, 2, 4)
        assert result.trap == 4
        assert result.min == 3
        assert result.max == 5

    def test_integrate_linear_decreasing(self):
        result = Integrator(lambda x: -2 * x, Mode.DECREASING)\
            .integrate(0, 2, 4)
        assert result.trap == -4
        assert result.min == -5
        assert result.max == -3

    def test_integrate_parabola(self):
        integrator = Integrator(lambda x: 3 * x ** 2)
        basic_result = integrator.integrate(-1, 1, 4)
        assert basic_result.trap == Decimal('2.25')
        assert basic_result.min == Decimal('0.75')
        assert basic_result.max == Decimal('3.75')

        messy_result = integrator.integrate(-1, 1, 5)
        assert messy_result.trap == Decimal('2.16')
        assert messy_result.min == Decimal('0.96')

    def test_calculate_circle_area(self):
        integrator = Integrator(lambda x: 4 * (1 - x ** 2) ** Decimal('0.5'),
                                Mode.DECREASING)
        first_approximation = integrator.integrate(0, 1, 10)
        assert round(first_approximation.trap, 1) == Decimal('3.1')
        assert first_approximation.max > first_approximation.min
        assert first_approximation.max - first_approximation.min < Decimal('0.5')

        second_approximation = integrator.integrate(0, 1, 100)
        assert round(second_approximation.trap, 2) == Decimal('3.14')
        assert second_approximation.max > second_approximation.min
        assert second_approximation.max - second_approximation.min \
               < Decimal('0.05')

    def test_calculate_circle_area_to_precision_one(self):
        integrator = Integrator(lambda x: 4 * (1 - x ** 2) ** Decimal('0.5'),
                                Mode.DECREASING)
        assert integrator.integral_to_precision(0, 1, 1, 2)[0] \
               == Decimal('3.1')

    def test_calculate_elliptic_integrals(self):
        # The result of integrating this function from 0 to 1 represents the
        # perimeter of an ellipse whose minor axis has length 1 and whose major
        # axis has length "a".
        # The integral from 0 to t of this function is
        # 2 * a * EllipticE(t, k)
        # where k = 1 - 1 / a^2
        def elliptic_function(a, s):
            return 2 * (
                (a ** 2 + (1 - a ** 2) * s ** 2) / (1 - s ** 2)
            ) ** Decimal('0.5')

        # Since the above function is undefined at a = 1 this error function
        # returns a distance "d" from 1 such that the integral from "1 - d" to
        # "1" of the above function is less than "error".
        # It uses a geometric notion to say that the arc length from
        # "x = a - ad" to "x = a" along the path of the ellipse is shorter than
        # the path that goes from (x, y) to (a, y) and then (a, 0).
        def error_function(a, error):
            return (
                1 + a * error
                - (1 + 2 * a * error - error ** 2) ** Decimal('0.5')
            ) / (a ** 2 + 1)

        def get_elliptic_integrator(a):
            return Integrator(
                lambda x: elliptic_function(a, x),
                Mode.DECREASING
            )

        elliptic_integrator_doubled = get_elliptic_integrator(2)
        assert elliptic_integrator_doubled.integral_to_precision(
                0, 1, precision=1, resolution=2,
                error_func_upper=lambda e: error_function(2, e)
            )[0] == Decimal('4.8')
        # The true value of 2 * 2 * EllipticE(1 - 1 / 2^2) is
        # 4.8442241102738380992142515981959147059769591989433004125415581762
