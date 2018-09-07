import dis
import sys


# def f(x, y):
#     x += y
#     print(x, y, 20)
#
#
# def g(x, y):
#     a = 10
#     b = x


# print(dis.dis(f))
# print(f.__code__.co_code)

# print(dis.dis(g))
# print(g.__code__.co_consts)
# print(g.__code__.co_names)
# print(g.__code__.co_varnames)

# help(compile)
# help(eval)
# help(exec)
# print(eval('x + y', {'x': 10, 'y': 20}))


class A:
    X = 1


class B:
    __slots__ = ['x']

    def __init__(self):
        self.x = 1

print(sys.getsizeof(1))  # Затраты в памяти
print(A.__dict__)
print(sys.getsizeof(A))  # Большие затраты в памяти, хранит dict
print(sys.getsizeof(A()))  # Гораздо меньший вес
print(sys.getsizeof(B))  # Оптимизация
print(sys.getsizeof(B()))  # Оптимизация




