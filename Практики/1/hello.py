for x1 in range(10):
    for x2 in range(10):
        for x3 in range(10):
            for x4 in range(10):
                for x5 in range(10):
                    z1 = x1 + x2 + x3 + x4 + x5 == 26
                    z2 = x1 * x2 == 24
                    z3 = x4 * 2 == x2
                    z4 = x1 + x3 == x2 + x4
                    if z1 and z2 and z3 and z4:
                        print(x1, x2, x3, x4, x5, sep='')
