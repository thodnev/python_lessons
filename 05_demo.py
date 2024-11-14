#!/usr/bin/env python3

import sys
import itertools


def process():
    ### BAD BAD BAD. As studied in schools. Incorrect practices

    # not itertools.takewhile
    col = []

    while True:
        try:
            data = input("Enter name ('' to end): ")
        except EOFError:
            break

        if not data:
            break

        col.append(data.title())

    return '\n'.join(sorted(col))


def process_impr():
    # data = sys.stdin.read()     # fully until EOF
    # return '\n'.join(map(str.title, sorted(data.splitlines())))
    print("Enter name ('' to end): ", end='', file=sys.stderr, flush=True)

    data = []
    for line in sys.stdin:
        if not line:
            break
        data.append(line.title())

    return ''.join(sorted(data))

    # def linegen():
    #     for line in sys.stdin:
    #         if not line:
    #             break
    #         yield line


def process_prof():
    lines = itertools.takewhile(lambda l: bool(l), sys.stdin)
    return ''.join(map(str.title, sorted(lines)))


if __name__ == '__main__':
    # statements gelow get executed
    # only when the module is used as toplevel (i.e. script)
    # when imported as library, this block won't run

    res = process_prof()
    print(res)

    # imitate error
    # raise Exception('IMITATING SERIOUS PROBLEM')
