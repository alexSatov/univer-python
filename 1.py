# z = list(itertools.islice(itertools.cycle([1, 2]), 0, 3))


def simple_numbers(n):
    a = [x for x in range(n + 1)]
    a[1] = 0
    i = 2
    while i <= n:
        if a[i] != 0:
            yield a[i]
            for j in range(i, n + 1, i):
                a[j] = 0
        i += 1


print([x for x in simple_numbers(100)])
