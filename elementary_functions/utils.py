from abc import abstractmethod
from typing import Protocol, List, runtime_checkable
from custom_numbers.types import Numeric


@runtime_checkable
class Function(Protocol):
    @abstractmethod
    def evaluate(self, x: Numeric) -> Numeric:
        """A function must be able to take an input and render an output"""
        raise NotImplementedError

    @abstractmethod
    def __mul__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __rmul__(self, other):
        """Allow functions to be scaled"""
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other):
        """Allow functions to be scaled"""
        raise NotImplementedError

    @abstractmethod
    def __matmul__(self, other):
        raise NotImplementedError


class FunctionSum:
    def __init__(self, *constituents):
        self.constituents: List[Function] = list(constituents)

    def __str__(self):
        return ' + '.join(map(str, self.constituents))

    def __repr__(self):
        return f'FunctionSum({",".join(map(str, self.constituents))})'

    def __eq__(self, other):
        if hasattr(other, 'constituents'):
            return set(self.constituents) == set(other.constituents)
        if len(self.constituents) == 0:
            return ConstantFunction() == other
        if len(self.constituents) > 1:
            return False
        return self.constituents[0] == other

    def evaluate(self, x: Numeric) -> Numeric:
        return sum(map(lambda f: f.evaluate(x), self.constituents))

    def __mul__(self, other):
        return sum(
            map(lambda f: other * f, self.constituents),
            ConstantFunction(),
        )

    def __rmul__(self, other):
        return FunctionSum(*map(lambda f: other * f, self.constituents))

    def __add__(self, other):
        if isinstance(other, FunctionSum):
            return FunctionSum(*(self.constituents + other.constituents))
        return FunctionSum(*self.constituents, other)

    def __matmul__(self, other):
        return FunctionSum(*map(
            lambda f: f @ other,
            self.constituents
        ))


class FunctionProd:
    def __init__(self, *constituents):
        self.constituents: List[Function] = list(constituents)

    def __str__(self):
        return ''.join(map(lambda x: f'({x})', self.constituents))

    def __repr__(self):
        return f'FunctionProd({",".join(map(str, self.constituents))})'

    def __eq__(self, other):
        if hasattr(other, 'constituents'):
            return set(self.constituents) == set(other.constituents)
        if len(self.constituents) == 0:
            return ConstantFunction(1) == other
        if len(self.constituents) > 1:
            return False
        return self.constituents[0] == other

    def evaluate(self, x: Numeric) -> Numeric:
        result = 1
        for f in self.constituents:
            result *= f.evaluate(x)
        return result

    def __rmul__(self, other):
        return FunctionProd(
            other * self.constituents[0],
            *self.constituents[1:],
        )

    def __add__(self, other):
        return FunctionSum(self, other)

    def __matmul__(self, other):
        return FunctionProd(*map(
            lambda f: f @ other,
            self.constituents,
        ))


class ConstantFunction:
    def __init__(self, val: Numeric = 0):
        self.val = val

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return f'ConstantFunction({self.val})'

    def __eq__(self, other):
        if isinstance(other, ConstantFunction):
            return self.val == other.val
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


class CompositeFunction:
    def __init__(self, outer: Function, inner: Function):
        self.outer = outer
        self.inner = inner

    def evaluate(self, x: Numeric) -> Numeric:
        return self.outer.evaluate(self.inner.evaluate(x))

    def __mul__(self, other):
        return FunctionProd(self, other)

    def __rmul__(self, other):
        return CompositeFunction(other * self.outer, self.inner)

    def __add__(self, other):
        return FunctionSum(self, other)

    def __matmul__(self, other):
        return CompositeFunction(self, other)
