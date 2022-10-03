from general.numbers import maximum


def vector_sum(l1, l2):
    result = []
    for i in range(maximum(len(l1), len(l2))):
        if len(l1) <= i:
            result.append(l2[i])
        elif len(l2) <= i:
            result.append(l1[i])
        else:
            result.append(l1[i] + l2[i])
    return result
