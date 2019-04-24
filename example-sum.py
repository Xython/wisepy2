from wisepy2 import *
import builtins
import sys


@wise
def sum(*args: int, to_float: bool = False, double: bool = False, additional_add: int):
    """
    my sum command
    """
    ret = builtins.sum(args)

    if double:
        ret = ret * 2

    if to_float:
        ret = float(ret)

    if additional_add:
        ret += additional_add
    print(ret)
    return 0


if __name__ == '__main__':
    sys.exit(sum(sys.argv[1:]))
