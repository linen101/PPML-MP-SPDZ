#program.use_edabit(True)
program.set_security(40)
program.set_bit_length(63)
from Compiler import  ml
from Compiler import types

clients = 50
#"""
n=100000
print('%d squarings and %d multiplications for cosine similarity' % (2*n,2*n))

a = (types.sint.get_random(size=n))
b = sint.get_random(size=n)
c = sint.get_random(size=1)
d = sint.get_random(size=1)

start_timer(1)
@for_range_opt(clients)
def _(i):
    c/d
    types.sint.square(a)
    types.sint.square(b)
    types.sint.dot_product(a,b)
    types.sint.dot_product(a,b)
stop_timer(1)   
#""" 

"""    
rounds=1000
c=sint.get_random(size=1)
start_timer(2)
#@for_range(rounds)
#def _(i):
@for_range_opt(clients)
def _(i):
    types.sint.max(0,c)
stop_timer(2)
"""