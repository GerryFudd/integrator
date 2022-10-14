from elementary_functions.calculus_utils import ConstantFunction, \
    DifferentiableFunction
from elementary_functions.simple import CharacteristicFunction, SimpleFunction
from elementary_functions.utils import Function, FunctionSum


def differentiate(func: Function):
    if isinstance(func, DifferentiableFunction):
        return func.differentiate()
    if isinstance(func, FunctionSum):
        return sum(
            map(lambda x: differentiate(x), func.constituents),
            ConstantFunction(),
        )
    if isinstance(func, CharacteristicFunction) \
            or isinstance(func, SimpleFunction):
        return ConstantFunction()
    raise NotImplementedError
