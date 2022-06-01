from time import perf_counter
t = perf_counter()
from ursina import *

app = Ursina()

print('----', perf_counter() - t)

app.run()
