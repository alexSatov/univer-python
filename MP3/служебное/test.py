with open("g.txt") as file:
    for line in file:
        line = line.strip()
        key, value = line.split(':')
        print('self.assertEqual("{}", info.info["{}"])'.format(value[1:], key))

# with open("g.txt") as file:
#     for line in file:
#         line = line.strip()
#         number, genre = line.split('.')
#         print('{}: \'{}\','.format(number, genre))

# a = b'\x00\x00\x00\x00'
# c = a.decode('ascii')
# print('"{}"'.format(c))

# b = b'+'
# print(b[0])

# I - 73
# T - 84

# from mp3 import bin_from_int, int_from_bytes
#
#
# b = b'\xff\xfb\x70\x50'
# print(bin_from_int(int_from_bytes(b), 32))

# b = b'\x21\x00\x00'
# print(b.find(b'\x00'))
