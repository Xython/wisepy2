from wisepy.talking import Talking
talking = Talking()


@talking
def add(left: 'an integer', right: 'another integer'):
    """
    add up two numbers.
    """
    left = int(left)
    right = int(right)
    return left + right


@talking.alias('sum')
def another(*args,
            to_float: bool = False,
            double=None,
            additional_add: int = None):
    """
    my sum command
    """

    # using type annotation in keyword argument makes the argument
    # cast to the specific type.

    ret = sum(map(int, args))

    if double:
        ret = ret * 2

    if to_float:
        ret = float(ret)

    if additional_add:
        ret += additional_add

    return ret


if __name__ == '__main__':
    talking.on()
