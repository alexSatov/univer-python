def donuts(count):
    if count > 9:
        return 'Number of donuts: many'
    else:
        return 'Number of donuts: {0}'.format(count)


def both_ends(string):
    if len(string) < 2:
        return ''
    else:
        return string[0:2] + string[-2:]


def fix_start(string):
    return string[0] + string[1:].replace(string[0], '*')


def mix_up(string_a, string_b):
    return string_b[0:2] + string_a[2:] + ' ' + string_a[0:2] + string_b[2:]


def verbing(string):
    if len(string) < 3:
        return string
    elif string[-3:] == 'ing':
        return string + 'ly'
    else:
        return string + 'ing'


def not_bad(string):
    start = string.find('not')
    end = string.find('bad')
    if start < end:
        return string[:start] + 'good' + string[end + 3:]
    else:
        return string


def front_back(string_a, string_b):
    a_front = string_a[:len(string_a) // 2 + len(string_a) % 2]
    a_back = string_a[-(len(string_a) // 2):]
    b_front = string_b[:len(string_b) // 2 + len(string_b) % 2]
    b_back = string_b[-(len(string_b) // 2):]
    return a_front + b_front + a_back + b_back


def test(got, expected):
    if got == expected:
        prefix = ' OK '
    else:
        prefix = '  X '
    print('{0} got: {1} expected: {2}'.format(prefix, repr(got),
                                              repr(expected)))


def main():
    print('donuts')
    # Each line calls donuts, compares its result to the expected
    # for that call.
    test(donuts(4), 'Number of donuts: 4')
    test(donuts(9), 'Number of donuts: 9')
    test(donuts(10), 'Number of donuts: many')
    test(donuts(99), 'Number of donuts: many')

    print()
    print('both_ends')
    test(both_ends('spring'), 'spng')
    test(both_ends('Hello'), 'Helo')
    test(both_ends('a'), '')
    test(both_ends('xyz'), 'xyyz')

    print()
    print('fix_start')
    test(fix_start('babble'), 'ba**le')
    test(fix_start('aardvark'), 'a*rdv*rk')
    test(fix_start('google'), 'goo*le')
    test(fix_start('donut'), 'donut')

    print()
    print('mix_up')
    test(mix_up('mix', 'pod'), 'pox mid')
    test(mix_up('dog', 'dinner'), 'dig donner')
    test(mix_up('gnash', 'sport'), 'spash gnort')
    test(mix_up('pezzy', 'firm'), 'fizzy perm')

    print()
    print('verbing')
    test(verbing('hail'), 'hailing')
    test(verbing('swiming'), 'swimingly')
    test(verbing('do'), 'do')

    print()
    print('not_bad')
    test(not_bad('This movie is not so bad'), 'This movie is good')
    test(not_bad('This dinner is not that bad!'), 'This dinner is good!')
    test(not_bad('This tea is not hot'), 'This tea is not hot')
    test(not_bad("It's bad yet not"), "It's bad yet not")

    print()
    print('front_back')
    test(front_back('abcd', 'xy'), 'abxcdy')
    test(front_back('abcde', 'xyz'), 'abcxydez')
    test(front_back('Kitten', 'Donut'), 'KitDontenut')


if __name__ == '__main__':
    main()
