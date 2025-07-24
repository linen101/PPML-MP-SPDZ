import math
fprecision = 16
sfix.set_precision(f=fprecision)

cfix.set_precision(f=fprecision)

x = sfix(2)
e = cfix(math.e)
y = e**x
print_ln('exp(%s)=%s',x.reveal(),y.reveal())