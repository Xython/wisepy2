from io import StringIO
from wisepy2 import wise
import sys
import typing

assert sys.version_info >= (3, 9), "this test requires Python 3.9+"


def ff(*, x: int):
    return x


res = wise(ff)(["--x", "2"])
print(res == 2)


def f(*, x: int = 1):
    return x


print(wise(f)([]))
try:
    import contextlib

    with contextlib.redirect_stderr(StringIO()):
        wise(f)(["a"])
    raise AssertionError("should not reach here")
except SystemExit:
    pass

# issue #2
res = wise(f)(["--x", "2"])
assert isinstance(res, int)

# issue #1
sys.argv.clear()
sys.argv.extend(["--x", "10"])
res = wise(f)([])
assert res == 1


class Top:
    @staticmethod
    def f1(c: int = 1):
        return c


assert wise(Top)(["f1"]) == 1
assert wise(Top)(["f1", "108"]) == 108
assert wise(Top)(["f1", "--c", "108"]) == 108
print(wise(Top)(["f1", "1"]))
print(wise(Top)(["f1", "a"]))
