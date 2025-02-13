import itertools
from Compiler import types, library, instructions
from Compiler import comparison, util
from Programs.Source import random_matrix

types.sfix.set_precision(16)  # Set _ fractional bits
program.set_bit_length(32)
sint = sbitint.get_type(32)

D = random_matrix.generate_array(100000,0,1)

""""
D = Matrix(5, 2, sfix)
D[0][0]=3
D[1][0]=6
D[2][0]=10
D[3][0]=5
D[4][0]=3

D[0][1]=5
D[1][1]=6
D[2][1]=5
D[3][1]=5
D[4][1]=1
"""
D.sort(batcher=False, n_bits=32)

#print_ln('sorted %s', D.reveal())

"""
n = 10000

h = types.Array.create_from(types.sint(types.regint.inc(n)))
l = types.Array.create_from(types.sint(types.regint.inc(n)))

shuffle = types.sint.get_secure_shuffle(len(h))
h_prime = h.get_vector().secure_permute(shuffle)
l_prime = l.get_vector().secure_permute(shuffle)

#print_ln('k_prime %s', h_prime.reveal())
"""



