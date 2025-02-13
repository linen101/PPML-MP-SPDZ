import itertools
from Compiler import types, library, instructions
from Compiler import comparison, util

types.sfix.set_precision(4)  # Set _ fractional bits
program.set_bit_length(8)
sint = sbitint.get_type(8)

#D = random_matrix.generate_array(10000,0,1)

D = Matrix(5, 2, sfix)
D[0][0]=3
D[1][0]=6
D[2][0]=7
D[3][0]=5
D[4][0]=3

D[0][1]=5
D[1][1]=6
D[2][1]=5
D[3][1]=5
D[4][1]=1

k = Array(5, sfix)
k[0]=3
k[1]=6
k[2]=7
k[3]=5
k[4]=3

def dest_comp(B):
    Bt = B.transpose()
    St_flat = Bt.get_vector().prefix_sum()
    Tt_flat = Bt.get_vector() * St_flat.get_vector()
    Tt = types.Matrix(*Bt.sizes, B.value_type)
    Tt.assign_vector(Tt_flat)
    return sum(Tt) - 1

def reveal_sort(k, D, reverse=False):
    """ Sort in place according to "perfect" key. The name hints at the fact
    that a random order of the keys is revealed.

    :param k: vector or Array of sint containing exactly :math:`0,\dots,n-1`
      in any order
    :param D: Array or MultiArray to sort
    :param reverse: wether :py:obj:`key` is a permutation in forward or
      backward order

    """
    comparison.require_ring_size(util.log2(len(k)) + 1, 'sorting')
    assert len(k) == len(D)
    library.break_point()
    shuffle = types.sint.get_secure_shuffle(len(k))
    #print_ln('sfuffle %s', shuffle.reveal())

    k_prime = k.get_vector().secure_permute(shuffle).reveal()
    #print_ln('k_prime %s', k_prime.reveal())


    idx = types.Array.create_from(k_prime)
    if reverse:
        D.assign_vector(D.get_slice_vector(idx))
        #print_ln('D_assignrev %s', D.reveal())
        library.break_point()
        D.secure_permute(shuffle, reverse=True)
        #print_ln('Dsecpermrev %s', D.reveal())
    else:
        D.secure_permute(shuffle)
        #print_ln('Dsecperm %s', D.reveal())
        library.break_point()
        v = D.get_vector()
        D.assign_slice_vector(idx, v)
        #print_ln('D_assign %s', D.reveal())
    library.break_point()
    instructions.delshuffle(shuffle)


def radix_sort(k, D, n_bits=None, signed=True):
    """ Sort in place according to key.

    :param k: keys (vector or Array of sint or sfix)
    :param D: Array or MultiArray to sort
    :param n_bits: number of bits in keys (int)
    :param signed: whether keys are signed (bool)

    """
    assert len(k) == len(D)
    bs = types.Matrix.create_from(k.get_vector().bit_decompose(n_bits))
    if signed and len(bs) > 1:
        bs[-1][:] = bs[-1][:].bit_not()
    radix_sort_from_matrix(bs, D)

def radix_sort_from_matrix(bs, D):
    n = len(D)
    for b in bs:
        assert(len(b) == n)
    B = types.sint.Matrix(n, 2)
    h = types.Array.create_from(types.sint(types.regint.inc(n)))
    @library.for_range(len(bs))

    def _(i):
        b = bs[i]
        print_ln('b %s', b.reveal())
        B.set_column(0, 1 - b.get_vector())
        B.set_column(1, b.get_vector())
        c = types.Array.create_from(dest_comp(B))

        reveal_sort(c, h, reverse=False)
        print_ln('c first %s', c.reveal())
        print_ln('h first %s', h.reveal())

        @library.if_e(i < len(bs) - 1)
        def _():
            #reveal_sort(h, bs[i + 1], reverse=True)
            print_ln('h second %s', h.reveal())
        @library.else_
        def _():
            reveal_sort(h, D, reverse=True)
            print_ln('h second %s', h.reveal())
            print_ln('sorted %s', D.reveal())


radix_sort(k,D,8)
