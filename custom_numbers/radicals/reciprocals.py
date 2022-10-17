from algebra.linear import LinearSystem, AffineSubspace


def p_square(
    p: int,
    left_vals: AffineSubspace = None,
    top_vals: AffineSubspace = None
) -> AffineSubspace:
    left_lookup = {}
    if left_vals:
        for i, c in enumerate(left_vals.free_variables):
            left_lookup[f'y[{c}]'] = i
    top_lookup = {}
    if top_vals:
        for i, c in enumerate(top_vals.free_variables):
            top_lookup[f'y[{c}]'] = i
    in_variables = sorted(set(
        list(left_lookup.keys()) + list(top_lookup.keys())
    ))
    variables = ['z']

    equations = []
    for i in range(p):
        for j in range(p):
            if i == 0 and j == 0:
                continue
            equation = [0] * (p**2 + len(in_variables))
            variables.append(f'a[{i},{j}]')
            if i == 0:
                for k, v in enumerate(in_variables):
                    if v in top_lookup:
                        equation[p**2+k] = top_vals \
                            .linear_subspace \
                            .matrix[j-1][top_lookup[v]]
            elif j == 0:
                for k, v in enumerate(in_variables):
                    if v in left_lookup:
                        equation[p**2+k] = left_vals \
                            .linear_subspace \
                            .matrix[i-1][left_lookup[v]]
            for n in range(p**2):
                a, b = divmod(n, p)
                if (a == i and b == j) \
                    or (a+1 == i and b == j) \
                    or (a == i and b+1 == j):
                    equation[n] = 1
            equations.append(equation)

    return LinearSystem.of(
        variables + in_variables,
        equations
    ).solve()
