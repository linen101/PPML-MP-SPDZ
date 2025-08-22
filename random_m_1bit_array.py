import math
from Compiler import types, library, instructions
from Compiler.types import Array, cfix, sint, cint
program.set_security(40)

def get_random_bits_with_sum(n, m):
    assert m <= n
    
    bits = types.Array(n, types.sint)
    @for_range_opt(m)
    def _(i):
        bits[i] = 1
        
    @for_range_opt(n-m)
    def _(i):
        bits[i] = 0   
    bits.shuffle()
    bits.reveal()
    return bits

bits = get_random_bits_with_sum(64,4)