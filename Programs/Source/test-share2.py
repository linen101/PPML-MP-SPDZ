from Compiler import types

a = Array(1, sint)
#a[0] = sint(5)
#a.write_to_file()
shares = sint.read_from_file(0,1)[1]
print_ln('%s',shares[0], print_secrets=Trues)