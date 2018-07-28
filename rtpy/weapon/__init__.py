try:
    from toolz import compose
except:
    from functools import reduce as _reduce


    def compose(*fns):
        if not fns:
            raise ValueError("empty function list.")

        def _inner(*args, **kwargs):
            return _reduce(lambda arg, fn: fn(arg), fns[-2::-1], fns[-1](*args, **kwargs))

        return _inner
