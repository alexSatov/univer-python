import numpy as np  # Модуль для быстрой работы с массивами
import matplotlib.pyplot as plt  # Модуль для построения графиков
from scipy.integrate import odeint  # Библиотека для интеграции


# Тут задаются уравнения
def construct_model(k=8, a=0.15, eps_0=0.002, mu_1=0.2, mu_2=0.3):
    def eps_fun(u, v):
        return eps_0 + mu_1*v/(u+mu_2)

    def fun(y, t):
        u, v = y
        eps = eps_fun(u,v)
        derivs = [-k*u*(u-a)*(u-1)-u*v,
                  eps*(-v-k*u*(u-a-1))]
        return derivs

    return fun


fun = construct_model()

t = np.linspace(0, 40, 1000)

y0 = (0.17, 0)

psoln = odeint(fun, y0, t)

#plt.plot(psoln[:, 0],psoln[:, 1])
plt.plot(t,psoln[:, 0])

plt.show()