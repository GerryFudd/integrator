from __future__ import annotations

from abc import abstractmethod, ABC
from decimal import Decimal
from typing import TypeVar, Protocol, runtime_checkable


@runtime_checkable
class Numeric(Protocol):
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __add__(self, other):
        pass

    @abstractmethod
    def __radd__(self, other):
        pass

    @abstractmethod
    def __mul__(self, other):
        pass

    @abstractmethod
    def __rmul__(self, other):
        pass

    @abstractmethod
    def __pow__(self, power, modulo=None):
        pass

    @abstractmethod
    def __sub__(self, other):
        pass

    @abstractmethod
    def __truediv__(self, other):
        pass

    @abstractmethod
    def __rtruediv__(self, other):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __ne__(self, other):
        pass

    @abstractmethod
    def __lt__(self, other):
        pass

    @abstractmethod
    def __le__(self, other):
        pass

    @abstractmethod
    def __gt__(self, other):
        pass

    @abstractmethod
    def __ge__(self, other):
        pass

    @abstractmethod
    def __neg__(self):
        pass

    @abstractmethod
    def __abs__(self):
        pass


@runtime_checkable
class Convertable(Protocol):
    @staticmethod
    @abstractmethod
    def of(x: Numeric) -> N:
        """Create a class instance from a numeric"""

    @abstractmethod
    def to_decimal(self) -> Decimal:
        """Converts this numeric class to a decimal"""


@runtime_checkable
class FlippableNumber(Protocol):
    @abstractmethod
    def flip(self: N) -> N:
        """
        This is applicable for ratios where self ** -1 may be constructed
        exactly.
        """


class NumericABC(ABC):
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __add__(self, other):
        pass

    @abstractmethod
    def __radd__(self, other):
        pass

    @abstractmethod
    def __mul__(self, other):
        pass

    @abstractmethod
    def __rmul__(self, other):
        pass

    @abstractmethod
    def __pow__(self, power, modulo=None):
        pass

    @abstractmethod
    def __sub__(self, other):
        pass

    @abstractmethod
    def __truediv__(self, other):
        pass

    @abstractmethod
    def __rtruediv__(self, other):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __ne__(self, other):
        pass

    @abstractmethod
    def __lt__(self, other):
        pass

    @abstractmethod
    def __le__(self, other):
        pass

    @abstractmethod
    def __gt__(self, other):
        pass

    @abstractmethod
    def __ge__(self, other):
        pass

    @abstractmethod
    def __neg__(self):
        pass

    @abstractmethod
    def __abs__(self):
        pass


class ConvertableNumberABC(NumericABC):
    @staticmethod
    @abstractmethod
    def of(x: Numeric) -> N:
        """Create a class instance from a numeric"""

    @abstractmethod
    def to_decimal(self) -> Decimal:
        """Converts this numeric class to a decimal"""


ComputationType = TypeVar('ComputationType', bound=Convertable)


N = TypeVar('N', bound=Convertable)
