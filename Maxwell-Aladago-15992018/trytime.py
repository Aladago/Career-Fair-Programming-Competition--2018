import time
from timeit import default_timer as t

t1 = time.time()
print([i for i in range(100)])
print(time.time() - t1)

t2 = t()
print([i for i in range(100)])
print(t() - t2)