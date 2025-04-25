#program.use_dabit = bool(int(program.args[1]))
#program.use_edabit(int(program.args[1]) == 2)
#program.use_split(3)

program.use_edabit(True)
print(program.use_dabit, program.use_edabit())

program.set_security(40)
program.set_bit_length(63)
from Compiler import  ml
from Compiler import types

n = 10322

res = sint.Array(n)

n_threads = 1

l = 1

try:
    n_threads = int(program.args[2])
except:
    pass

try:
    n = int(program.args[3])
except:
    pass

try:
    l = int(program.args[4])
except:
    pass

print('%d comparisons in %d threads and %d rounds' % (n, n_threads, l))

a = sint.get_random(size=100)
"""
start_timer(1)
@multithread(n_threads, n)
def _(base, m):
    @for_range(l)
    def _(i):
        (sint(0, size=m) < sint(1, size=m)).store_in_mem(base)
stop_timer(1)   
"""     

#"""
n=100
start_timer(8)
@for_range_opt(n)
def _(i):
        ml.argmax(a)
stop_timer(8)        
#"""
"""
start_timer(9)
@for_range_opt(n)
def _(i):
    tree_reduce_multithread(n_threads, lambda x, y: x.max(y), a_values)
stop_timer(9)        
"""