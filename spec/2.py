from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import numpy as np
from matplotlib import cm
from matplotlib import pyplot as plt

# 3 занятие

'''
графики
x = np.linspace(-10, 10, 1000)
y = x ** 3
z = 1000*x
plt.plot(x, y, color='saddlebrown', linewidth=10)
plt.plot(x, z, 'r+')
plt.scatter(z, y)
plt.show()
'''

'''
спираль
r = np.arange(0, 3.0, 0.01)
theta = 2 * np.pi * r
ax = plt.subplot(111, projection='polar')
ax.plot(theta, r, color='red', linewidth=3)
ax.set_rmax(2.0)
ax.grid(True)
ax.set_title('Line', va='bottom')
plt.show()
'''

'''
скаттер
n = 50
x = np.random.normal(size=n)
y = np.random.uniform(size=n)
color = np.random.rand(n)
area = np.pi * (15 * np.random.rand(n))**2
plt.scatter(x, y, s=area, c=color, alpha=0.5)
plt.show()
'''

'''
3D фигуры
step = 0.04
maxval = 1.0
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# create supporting points in polar coordinates
r = np.linspace(0, 1.25, 50)
p = np.linspace(0, 2*np.pi, 50)
R, P = np.meshgrid(r, p)
# transform them to cartesian system
X, Y = R*np.cos(P), R*np.sin(P)

Z = ((R**2 - 1)**2)
ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.YlGnBu_r)
ax.set_zlim3d(0, 1)
ax.set_xlabel(r'$\phi_\mathrm{real}$')
ax.set_ylabel(r'$\phi_\mathrm{im}$')
ax.set_zlabel(r'$V(\phi)$')
plt.show()
'''

a = np.matrix([[1,0], [0,2]])
b = np.linalg.eig(a)[0]
print(b)