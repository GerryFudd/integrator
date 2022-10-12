from custom_numbers.exact.types import ExactNumber
from custom_numbers.radicals.radical_sum import RadicalSum
from custom_numbers.types import Numeric


def to_exact(x: Numeric) -> ExactNumber:
    return RadicalSum.of(x)
