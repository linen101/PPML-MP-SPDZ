from Compiler import types

s1 = sint(7)

print_ln('Shared s1: %s', s1, print_secrets=True)

a = types.sint.get_input_from(0)
print_ln(' a: %s', a.reveal(), print_secrets=True)

b = types.sint.get_input_from(1)
print_ln(' b: %s', b.reveal(), print_secrets=True)

#types.sint.write_to_file(b)

a1  = types.sint.read_from_file(1,1)[1][0]

print_ln('secrets a: %s', a, print_secrets=True)

print_ln('secrets b: %s', b, print_secrets=True)

print_ln('secrets a1: %s', a1, print_secrets=True)
