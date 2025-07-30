import math
fprecision = 16
sfix.set_precision(f=fprecision)

cfix.set_precision(f=fprecision)
#cfix.round_nearest = True
e = cfix(math.e)
"""
x = cfix(-15)
start_timer(1)
y = (e**x)
stop_timer(1)
print_ln('exp(%s)=%s',x,y.reveal())
"""
x = sint(-1)
x_exp= (x<0).if_else(x,-x)
e_x = e**x_exp
print_ln('1: exp(%s)=%s',x_exp.reveal(),e_x.reveal())

x_exp = -abs(x)
e_x = e**x_exp
print_ln('2: exp(%s)=%s',x_exp.reveal(),e_x.reveal())

x_exp = x
e_x = e**x_exp
print_ln('3: exp(%s)=%s',x_exp.reveal(),e_x.reveal())

x_exp = sint(-1)
e_x = e**x_exp
print_ln('4: exp(%s)=%s',x_exp.reveal(),e_x.reveal())

x_exp = sfix(-1)
e_x = e**x_exp
print_ln('5: exp(%s)=%s',x_exp.reveal(),e_x.reveal())

x_exp = sfix(-abs(x))
e_x = e**x_exp
print_ln('6: exp(%s)=%s',x_exp.reveal(),e_x.reveal())



#print_ln(y)