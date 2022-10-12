from __future__ import annotations
from abc import abstractmethod, ABC
from typing import List

from custom_numbers.types import Numeric
from elementary_functions.utils import FunctionSum, FunctionProd, \
    CompositeFunction, Function


class DifferentiableFunction(Function, ABC):
    @abstractmethod
    def differentiate(self) -> DifferentiableFunction:
        """Returns the derivative function"""


class DifferentiableSum(FunctionSum, DifferentiableFunction):
    constituents: List[DifferentiableFunction]

    def __init__(self, *constituents: DifferentiableFunction):
        for constituent in constituents:
            if not isinstance(constituent, DifferentiableFunction):
                raise NotImplementedError
        FunctionSum.__init__(self, *constituents)

    def differentiate(self) -> DifferentiableFunction:
        return DifferentiableSum(*filter(
            lambda x: x != ConstantFunction(),
            map(lambda f: f.differentiate(), self.constituents)
        ))


class DifferentiableProd(FunctionProd, DifferentiableFunction):
    constituents: List[DifferentiableFunction]

    def __init__(self, *constituents: DifferentiableFunction):
        for constituent in constituents:
            if not isinstance(constituent, DifferentiableFunction):
                raise NotImplementedError
        FunctionProd.__init__(self, *constituents)

    def differentiate(self) -> DifferentiableFunction:
        constituents = []
        for n in range(len(self.constituents)):
            constituents.append(DifferentiableProd(*(
                self.constituents[:n]
                + [self.constituents[n].differentiate()]
                + self.constituents[n+1:]
            )))
        return DifferentiableSum(*constituents)


class DifferentiableComposite(CompositeFunction, DifferentiableFunction):
    outer: DifferentiableFunction
    inner: DifferentiableFunction

    def __init__(
        self, outer: DifferentiableFunction, inner: DifferentiableFunction,
    ):
        for constituent in (outer, inner):
            if not isinstance(constituent, DifferentiableFunction):
                raise NotImplementedError
        CompositeFunction.__init__(self, outer, inner)

    def differentiate(self) -> DifferentiableFunction:
        return DifferentiableProd(
            self.inner.differentiate(),
            DifferentiableComposite(self.outer.differentiate(), self.inner),
        )


class ConstantFunction(DifferentiableFunction):
    def differentiate(self) -> DifferentiableFunction:
        return ConstantFunction()

    def __init__(self, val: Numeric = 0):
        self.val = val

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return f'ConstantFunction({self.val})'

    def __eq__(self, other):
        if isinstance(other, ConstantFunction):
            return self.val == other.val
        if isinstance(other, FunctionSum):
            if len(other.constituents) > 1:
                return False
            if len(other.constituents) == 1:
                return other.constituents[0] == self
            return self.val == 0
        if isinstance(other, FunctionProd):
            if len(other.constituents) > 1:
                return False
            if len(other.constituents) == 1:
                return other.constituents[0] == self
            return self.val == 1
        return other == self

    def evaluate(self, x: Numeric) -> Numeric:
        return self.val

    def __mul__(self, other):
        return self.val * other

    def __rmul__(self, other):
        return ConstantFunction(other * self.val)

    def __add__(self, other):
        if self.val == 0:
            return other
        return FunctionSum(self, other)

    def __matmul__(self, other):
        return self
