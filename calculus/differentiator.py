from elementary_functions.polynomial import Polynomial
from elementary_functions.power import PowerFunction
from elementary_functions.simple import CharacteristicFunction, SimpleFunction
from elementary_functions.utils import Function, FunctionSum, ConstantFunction


def differentiate(func: Function):
    if isinstance(func, PowerFunction):
        return PowerFunction(func.power - 1, func.coefficient * func.power)
    if isinstance(func, FunctionSum):
        return sum(
            map(lambda x: differentiate(x), func.constituents),
            ConstantFunction(),
        )
    if isinstance(func, Polynomial):
        new_coefficients = []
        for i, c in enumerate(func.coefficients):
            if i == 0:
                continue
            new_coefficients.append(i * c)
        return Polynomial(*new_coefficients)
    if isinstance(func, CharacteristicFunction) \
            or isinstance(func, SimpleFunction):
        return ConstantFunction()
    raise NotImplementedError
