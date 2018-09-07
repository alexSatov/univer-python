import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from scipy.optimize import fsolve

p = 3
shift = 1.0

# Создание функции


def construct_fun(p=2, shift=1.0):
   def f(pack):
        x, y = pack
        u = np.array([y - x**p, y - x - shift])
        return u
   return f

# Решение
F = construct_fun(p=p)
result = fsolve(F, [1.0, 2.0])
print(result)

# Построение графика

fig, ax = plt.subplots()
plt.xlim(-3, 3)
plt.ylim(-3, 3)
plt.gca().set_aspect('equal', adjustable='box')
plt.subplots_adjust(bottom=0.25)

x = np.linspace(-4, 4, 100)
y1 = x**p
y2 = x + shift

plt.plot(x,y1)
l, = plt.plot(x,y2)
sol, = plt.plot([result[0]],[result[1]], 'o')

axcolor = 'lightgoldenrodyellow'
sld_place = plt.axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)
sld = Slider(sld_place, "Shift", -3.0, 3.0, valinit=shift)

def update(val):
    print(sld.val)
    shift_ = sld.val
    y2 = x + shift_

    l.set_ydata(y2)

    F = construct_fun(p=p, shift=shift_)
    result = fsolve(F, [1.0, 2.0])
    print(result)
    sol.set_xdata([result[0]])
    sol.set_ydata([result[1]])



sld.on_changed(update)


plt.show()

# Построение графика
#x = np.linspace(-4, 4, 100)
#
#y1 = x**p
#y2 = x + shift
#
#plt.figure()
#plt.xlim(-3, 3)
#plt.ylim(-3, 3)
#plt.gca().set_aspect('equal', adjustable='box')
#
#plt.plot(x,y1)
#plt.plot(x,y2)
#plt.scatter([result[0]],[result[1]])
#
#plt.axvline(x=0, color='grey')
#plt.axhline(y=0, color='grey')
#plt.show()
#
#
#
