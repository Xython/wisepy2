from rtpy.cmd.talking import Talking

talking = Talking()


@talking
def add(left, right):
    left = int(left)
    right = int(right)
    return left + right


@talking.alias('sum')
def another(*args, to_float: bool = False, double=None,
            additional_add: 'specify some number to accumulate with at the final result' = None):
    # using type annotation in keyword argument makes the argument
    # cast to the specific type.

    ret = sum(map(int, args))

    if double:
        ret = ret * 2

    if to_float:
        ret = float(ret)

    if additional_add:
        ret += eval(additional_add)

    return ret


if __name__ == '__main__':
    import sys

    talking.from_text(' '.join(sys.argv[1:]))
