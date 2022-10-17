from algebra.linear.equations import MultiDimensionalEquation
from algebra.linear.subspace import AffineSubspace, LinearSubspace, \
    LinearSystem, Point


def p_square(
    p: int,
    left_vals: LinearSubspace = None,
    top_vals: LinearSubspace = None,
    symbol: str = 'a',
) -> AffineSubspace:
    variables = []
    end_variables = [f'{symbol}[0,0]']
    equation_mappings = []
    for i in range(p):
        for j in range(p):
            if i == 0 and j == 0:
                continue
            variables.append(f'{symbol}[{i},{j}]')
            equation_mapping = {}
            if i == 0:
                if top_vals:
                    for k, in_var, c in top_vals.matrix[j-1]:
                        equation_mapping[in_var] = c
                        if in_var not in end_variables:
                            end_variables.append(in_var)
            elif j == 0:
                if left_vals:
                    for k, in_var, c in left_vals.matrix[i-1]:
                        equation_mapping[in_var] = c
                        if in_var not in end_variables:
                            end_variables.append(in_var)
            for n in range(p**2):
                a, b = divmod(n, p)
                if (a == i and b == j) \
                        or (a+1 == i and b == j) \
                        or (a == i and b+1 == j):
                    equation_mapping[f'{symbol}[{a},{b}]'] = 1
            equation_mappings.append(equation_mapping)

    variables += end_variables

    return LinearSystem(*map(
        lambda eq_map: MultiDimensionalEquation(eq_map, 0, variables),
        equation_mappings,
    )).solve()


def solve_left_side(p: int) -> AffineSubspace:
    squares = []
    current = p_square(p, symbol=f'a{len(squares)}')
    squares.append(current)
    while len(current.free_variables) < p:
        current = p_square(
            p,
            top_vals=LinearSubspace(
                current.constrained_variables[-p+1:],
                current.free_variables,
                current.linear_subspace.matrix[-p+1:],
            ),
            symbol=f'a{len(squares)}'
        )
        squares.append(current)

    fixed_values_mapping = {}
    fixed_values = []
    for out_var in current.constrained_variables[-p+1:]:
        fixed_values_mapping[out_var] = 0
        fixed_values.append(out_var)

    result = squares[0]
    for square in squares[1:]:
        result @= square

    return result @ Point(fixed_values_mapping, fixed_values)
