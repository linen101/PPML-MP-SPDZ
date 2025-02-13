program.use_edabit(True)

import itertools
from Compiler import types, library, instructions
from Compiler import comparison, util
from Programs.Source import random_matrix

types.sfix.set_precision(4)  # Set 4 fractional bits

D = random_matrix.generate_array(10,0,1)

D.sort()

#print_ln('sorted %s', D.reveal())
