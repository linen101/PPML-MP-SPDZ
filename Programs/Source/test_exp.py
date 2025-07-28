import math
fprecision = 16
sfix.set_precision(f=fprecision)

cfix.set_precision(f=fprecision)
cfix.round_nearest = True

x = cfix(-15)
e = cfix(math.e)
start_timer(1)
y = (e**x)
stop_timer(1)
print_ln('exp(%s)=%s',x,y.reveal())
#print_ln(y)