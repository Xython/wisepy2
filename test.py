from wisepy2 import wise
import sys

assert sys.version_info >= (3, 9), "this test requires Python 3.9+"

def f(*, x: int = 1):
    return x

# issue #2
res = wise(f)(['--x', '2'])
assert isinstance(res, int)

# issue #1
sys.argv.clear()
sys.argv.extend(['--x', '10'])
res = wise(f)([])
assert res == 1
