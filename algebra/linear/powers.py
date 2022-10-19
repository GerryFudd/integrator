from algebra.linear.equations import MultiDimensionalEquation
from algebra.linear.subspace import AffineSubspace, LinearSystem, Point


def p_square(
    p: int,
    symbol: str = 'a',
    seed: list[MultiDimensionalEquation] = None,
    top_vars: list[str] = None,
    left_vars: list[str] = None,
) -> AffineSubspace:
    variables = []
    if top_vars:
        variables += top_vars
    if left_vars:
        variables += left_vars
    end_variables = [f'{symbol}[0,0]']
    equation_mappings = []
    for i in range(p):
        for j in range(p):
            if i == 0 and j == 0:
                continue
            variables.append(f'{symbol}[{i},{j}]')
            equation_mapping = {}
            if i == 0:
                if top_vars:
                    equation_mapping[top_vars[j-1]] = 1
            elif j == 0:
                if left_vars:
                    equation_mapping[left_vars[i-1]] = 1
            for n in range(p**2):
                a, b = divmod(n, p)
                if (a == i and b == j) \
                        or (a+1 == i and b == j) \
                        or (a == i and b+1 == j):
                    equation_mapping[f'{symbol}[{a},{b}]'] = 1
            equation_mappings.append((equation_mapping, 0))
    if seed:
        for eq in seed:
            for v in eq.variables:
                if v not in variables and v not in end_variables:
                    end_variables.append(v)
    variables += end_variables
    seed_equations = map(lambda x: x.with_variables(variables), seed) if seed else ()

    return LinearSystem(*seed_equations, *map(
        lambda eq_map: MultiDimensionalEquation(
            eq_map[0], eq_map[1], variables,
        ),
        equation_mappings,
    )).solve()


def solve_left_side(p: int) -> AffineSubspace:
    squares = []
    current = p_square(p, symbol=f'a{len(squares)}')
    squares.append(current)
    while len(current.free_variables) < p:
        top_vars = current.constrained_variables[-p+1:]
        next_seed_variables = top_vars + current.free_variables
        next_seed = list(map(
            lambda x: x.with_variables(top_vars + current.free_variables),
            filter(
                lambda x: any([x.val(v) != 0 for v in next_seed_variables]),
                current.linear_system.equations[-p+1:]
            )
        ))
        current = p_square(
            p,
            seed=next_seed,
            top_vars=top_vars,
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
