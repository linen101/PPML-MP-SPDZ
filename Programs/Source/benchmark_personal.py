import itertools
import random
import math
from Compiler import types, library, instructions
from Compiler import comparison, util
from Compiler import ml
from Programs.Source import random_matrix

# Set global precision for sfix
fprecision = 16
sfix.set_precision(f=fprecision)

# personal(player, Array(n, cint))
# Array value known to one player. 
# Supports operations with public values and personal values known to the same player. 
# Can be used with print_ln_to(). It is possible to convert to secret types like sint.
# Parameters: 
    # player – player (int)
    # # value – cleartext value (cint, cfix, cfloat) or array thereof
# Local computations on each party with types.personal have some limitations.
# In MP-SPDZ it is not possible to run  codes, which contain control flows, locally only on some parties owning the associating data.. 
# !!! The general design is that the high-level code runs in sync on all parties !!! 
# Operations on personal values are run "dryly" on parties where the value isn't present so it still fits the design. 
# You can think of the Python code running on the arithmetic black-box that MPC provides whereas the actual protocol runs on the C++ level.


"""
s_0 = sint(0)
v0 = s_0.reveal_to(1)

val_0 = types.personal(0, cint(0))
val_1 = types.personal(0, cint(1))
cint(0) * val_1
check_point()
"""

###   test generation of random uniform array for a player ###
def generate_random_shared_array(n, alpha, beta):
    # Set global precision for sfix...
    matrix_a = types.Array(n, types.sfix)
    @for_range_opt(n)
    def _(i):
        value = random.uniform(alpha, beta)
        value_sfix =  types.sfix(value)
        matrix_a[i] = value_sfix
    return matrix_a 

#a = generate_random_shared_array(10, 0, 1);

#a0 = a.reveal_to(player=0)

def generate_personal_array(player, length, alpha, beta):
    array_a = types.personal(player, Array(length, types.cfix))
    @for_range_opt(length)
    def _(i):
        value = random.uniform(alpha, beta)
        value_cfix =  types.cfix(value)
        array_a[i] = value_cfix
    return array_a  


def share_personal_array(array_a, length, alpha, beta):
    array_sa = Array(length, types.sfix)
    @for_range_opt(length)
    def _(i):
        svalue = sfix(array_a[i])
        array_sa[i] = svalue
    return array_sa  

"""


array_a = generate_personal_array(player = 0, length = 10, alpha =0,   beta=1)

array_sa = share_personal_array(array_a, length, alpha, beta)
"""
def generate_personal_matrix(player, d, alpha, beta):
    matrix_a = types.personal(player, Matrix(d, d, types.cfix))
    @for_range_opt(d)
    def _(i):
        @for_range_opt(d)
        def _(j):
            value = random.uniform(alpha, beta)
            value_cfix =  types.cfix(value)
            matrix_a[i][j] = value_cfix
    return matrix_a  


def share_personal_matrix(matrix_a, d, alpha, beta):
    matrix_sa = Matrix(d, d, types.sfix)
    @for_range_opt(d)
    def _(i):
        @for_range_opt(d)
        def _(j):
            svalue = sfix(matrix_a[i][j])
            matrix_sa[i] = svalue
    return matrix_sa  

d = 10
alpha =0
beta =1

matrix_a = generate_personal_matrix(player = 0, d = 10, alpha =0,   beta=1)

start_timer(1)
matrix_sa = share_personal_matrix(matrix_a, 10, alpha, beta)
stop_timer(1)