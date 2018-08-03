def dynamic_cast(fn: 'function'):
    annotations = fn.__annotations__

    def cast(k, v):
        ty = annotations.get(k)
        if isinstance(ty, type):
            v = ty(v)
        return v

    def inner(*args, **kwargs):
        kwargs = {k: cast(k, v) for k, v in kwargs.items()}
        return fn(*args, **kwargs)

    return inner
