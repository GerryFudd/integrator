from __future__ import annotations

from abc import ABC
from decimal import Decimal
from typing import Callable

from custom_numbers.exact.rational_number import RationalNumber
from custom_numbers.exact.types import ExactNumber


class BaseExactNumber(ExactNumber, ABC):
    @staticmethod
    def do_for_builtins(
        other,
        action: Callable[[ExactNumber], ExactNumber],
        or_else: Callable[[], any]
    ):
        if isinstance(other, int) \
                or isinstance(other, float) \
                or isinstance(other, Decimal):
            return action(RationalNumber.of(other))
        return or_else()
