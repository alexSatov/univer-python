import numpy as np

# 2 занятие
s = np.arange(1, 145, 0.23)


m = np.matrix(([1, 2], [3, 4]))
m1 = np.matrix(np.eye(10, dtype=int))
# ravel - матрица в массив

a = np.random.random((5, 2))
b = a.reshape(2,5)

# transpose - транспонирование
# np.linalg.inv
# np.__config__.show()


A = np.matrix(([1,2], [2, 3]))
b = np.matrix([[6], [7]])
x = np.linalg.solve(A, b)

print(s)