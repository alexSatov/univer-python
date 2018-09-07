# import struct
# pack/unpack

# Сериализация
# import json для читабельности
import marshal
import json
import pickle
import timeit


def check_marshal():
    a = [i for i in range(1000)]
    b = marshal.dumps(a)
    print(len(b))
    print(timeit.timeit(marshal.dumps(a), number=10000))
    c = marshal.loads(b)
    print(c)


def check_json():
    a = [i for i in range(1000)]
    b = json.dumps(a)
    print(len(b))
    print(timeit.timeit(json.dumps(a), number=10000))
    c = json.loads(b)
    print(c)


def check_pickle():
    a = [i for i in range(1000)]
    b = pickle.dumps(a)
    print(len(b))
    print(timeit.timeit(pickle.dumps(a), number=10000))
    c = pickle.loads(b)
    print(c)


check_json()
check_marshal()
check_pickle()



