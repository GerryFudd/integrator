from calculus.utils import maximum


class Polynomial:
    def __init__(self, *coefficients):
        self.coefficients = list(coefficients)

    def __eq__(self, other):
        if not isinstance(other, Polynomial):
            return False
        return self.coefficients == other.coefficients

    def __str__(self):
        result = []
        result.pop()
        for n in range(len(self.coefficients)):
            if self.coefficients[n] == 0:
                pass
            elif n == 0:
                result.append(f'{self.coefficients[0]}')
            elif n == 1:
                result.append(f'{self.coefficients[1]}x')
            elif n >= 10:
                result.append(f'{self.coefficients[n]}x^({n})')
            else:
                result.append(f'{self.coefficients[n]}x^{n}')
        return ' + '.join(result)

    def __repr__(self):
        return f'Polynomial(coefficients={self.coefficients})'

    def __reduce(self):
        while self.coefficients[-1] == 0:
            self.coefficients.pop()
        return self

    def plus(self, summand):
        coefficients = []
        for n in range(maximum(
            len(self.coefficients), len(summand.coefficients)
        )):
            if n >= len(self.coefficients):
                coefficients.append(summand.coefficients[n])
            elif n >= len(summand.coefficients):
                coefficients.append(self.coefficients[n])
            else:
                coefficients.append(
                    self.coefficients[n] + summand.coefficients[n]
                )
        return Polynomial(*coefficients).__reduce()

    def times(self, multiplicand):
        self.__reduce()
        multiplicand.__reduce()
        coefficients = []
        for n in range(len(self.coefficients)):
            for m in range(len(multiplicand.coefficients)):
                i = n + m
                if i < len(coefficients):
                    coefficients[i] = coefficients[i] \
                                      + self.coefficients[n] \
                                      * multiplicand.coefficients[m]
                else:
                    coefficients.insert(
                        i, self.coefficients[n] * multiplicand.coefficients[m]
                    )
        return Polynomial(*coefficients)
