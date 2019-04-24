from wisepy2 import *
import sys


@wise
def add(left: int, right: int):
    """
    add up two numbers.
    """
    print(left + right)
    return 0


if __name__ == '__main__':
    sys.exit(add(sys.argv[1:]))
