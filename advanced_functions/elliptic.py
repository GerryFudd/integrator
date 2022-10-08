from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction


from general.numbers import Numeric, Number


class EllipticFunction:
    def __init__(self, a: Numeric):
        self.a = Number.of(a)
        self.func = 2 * (
            PowerFunction(0.5) @ Polynomial(self.a ** 2, 0, 1 - self.a ** 2)
        ) * (PowerFunction(-0.5) @ Polynomial(1, 0, -1))

    # The result of integrating this function from 0 to 1 represents the
    # perimeter of an ellipse whose minor axis has length 1 and whose major
    # axis has length "a".
    # The integral from 0 to t of this function is
    # 2 * a * EllipticE(t, k)
    # where k = 1 - 1 / a^2
    def evaluate(self, x: Numeric) -> Numeric:
        return 2 * (
            (self.a ** 2 + (1 - self.a ** 2) * Number.of(x) ** 2)
            / (1 - x ** 2)
        ) ** 0.5

    # Since the elliptic function is undefined at a = 1 this error function
    # returns a distance "d" from 1 such that the integral from "1 - d" to
    # "1" of the above function is less than "error".
    # It uses a geometric notion to say that the arc length from
    # "x = a - ad" to "x = a" along the path of the ellipse is shorter than
    # the path that goes from (x, y) to (a, y) and then (a, 0).
    def error_function(self, error):
        return (
            1 + self.a * error
            - (1 + 2 * self.a * error - error ** 2) ** 0.5
        ) / (self.a ** 2 + 1)
