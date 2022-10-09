from __future__ import annotations

from abc import abstractmethod
from decimal import Decimal
from typing import runtime_checkable, Protocol, TypeVar


@runtime_checkable
class Numeric(Protocol):
    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __radd__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __mul__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rmul__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __pow__(self, power, modulo=None):
        raise NotImplementedError

    @abstractmethod
    def __sub__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __truediv__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rtruediv__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __ne__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __le__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __gt__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __ge__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __neg__(self):
        raise NotImplementedError

    @abstractmethod
    def __abs__(self):
        raise NotImplementedError


N = TypeVar('N')


@runtime_checkable
class ConvertableNumber(Protocol):
    @abstractmethod
    def of(self: N, x: Numeric) -> N:
        raise NotImplementedError

    @abstractmethod
    def to_decimal(self) -> Decimal:
        raise NotImplementedError

    @abstractmethod
    def to_float(self) -> float:
        raise NotImplementedError


@runtime_checkable
class FlippableNumber(Protocol):
    @abstractmethod
    def flip(self: N) -> N:
        raise NotImplementedError


ComputationType = TypeVar('ComputationType')
