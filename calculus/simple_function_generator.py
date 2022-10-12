from custom_numbers.exact.factory import to_exact
from elementary_functions.utils import Function
from general.interval import Interval


def image_under_func(func: Function, interval: Interval):
    initial_value = func.evaluate(to_exact(interval.a))

