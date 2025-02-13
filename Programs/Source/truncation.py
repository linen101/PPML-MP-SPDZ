import itertools
import random
from Compiler import types, library, instructions
from Compiler import comparison, util


decimal_precision = 8

#types.sfix.set_precision(decimal_precision)  # Set _ fractional bits

# bit length of S_k, much smaller than bit-length of mp-spdz
k = 8
d = 2
l = 20
x = sint(2**5)

# number of parties
m = 3



def fixed_point_preprocessing(k, l, d):
    # Step 1: Generate random number r_i
    lower_bound = 1
    upper_bound = 2 ** (k+l)

    r_i = random.randint(lower_bound, upper_bound)
    trunc_d = 2**d  # Example fixed-point precision divisor

    # Step 2: Perform truncation (dividing by d)
    r_i_d = r_i // trunc_d  # Integer division, truncation to simulate fixed-point precision

    r_i_share = sint(r_i)
    r_i_d_share= sint(r_i_d)
    # Print or log for debugging
    print_ln('value r: %s', r_i)
    print_ln('truncated random value r/d: %s', r_i_d)
    
    # Step 3: Each party sums their shares ( handled by MP-SPDZ ?)
    # These variables represent shared sums across all parties ?
    r_sum = r_i_share  # For simplicity in this example
    r_d_sum = r_i_d_share

    # Print or log for debugging
    print_ln('Shared random value r: %s', r_sum.reveal())
    print_ln('Truncated random value r/d: %s', r_d_sum.reveal())

    return r_sum, r_d_sum

# Call the function to simulate the protocol
#fixed_point_preprocessing(k,l,d)
    
def trunc(x, d, k, l):
    """Truncation protocol for secret-shared fixed-point integer x."""
    #w = sint(0)
    trunc_divisor = 2**d
    r_sum, r_trunc_sum = fixed_point_preprocessing(k, l, d)

    
    # Perform the truncation
    w = x + r_sum
    w_revealed = w.reveal()  # Reveal w for truncation
    print_ln('w: %s', w_revealed)
    w_trunc = w_revealed / trunc_divisor
    print_ln('w_trunc: %s', w_trunc)

    # Compute the final result by subtracting the aggregate truncation shares
    z = w_trunc - r_trunc_sum
    return z


z = trunc(x, d, k, l)
print_ln('truncated x=%s', z.reveal())


def test_trunc_default():
    a=sfix(-2**13)
    b=sfix(2**13)
    c=a*b
    print_ln('a: %s', a.reveal())
    print_ln('b: %s', b.reveal())
    print_ln('c: %s', c.reveal())
    return c

test_trunc_default()    
    
for i in 0, 1:
    print_ln('got %s from player %s', sint.get_input_from(i).reveal(), i)