import inspect
import types
import argparse

__all__ = ['wise']


def process_empty(x):
    if x is inspect._empty:
        return None
    return x


class _Colored:
    Red = '\033[31m'
    Green = '\033[32m'
    Yellow = '\033[33m'
    Blue = '\033[34m'
    Purple = '\033[35m'
    LightBlue = '\033[36m'
    Clear = '\033[39m'
    Purple2 = '\033[95m'


def _wrap_color(colored: str):
    def func(*strings: str, sep=''):
        strings = map(lambda each: f'{colored}{each}', strings)
        return f'{sep.join(strings)}{_Colored.Clear}'

    return func


Red = _wrap_color(_Colored.Red)
Green = _wrap_color(_Colored.Green)
Yellow = _wrap_color(_Colored.Yellow)
Blue = _wrap_color(_Colored.Blue)
Purple = _wrap_color(_Colored.Purple)
LightBlue = _wrap_color(_Colored.LightBlue)
Purple2 = _wrap_color(_Colored.Purple2)


def _describe_parameter(p: inspect.Parameter):
    kind = p.kind
    name = p.name
    anno = process_empty(p.annotation)
    default = process_empty(p.default)

    args = []
    kwargs = {}
    accept = None

    if anno:
        if anno is bool and isinstance(default, bool):
            kwargs['action'] = 'store_false' if default else 'store_true'
        elif type(anno) is type:
            kwargs['type'] = anno
        kwargs['help'] = Blue(str(anno))

    if default:
        kwargs['default'] = default

    if kind is inspect.Parameter.POSITIONAL_ONLY:
        args.append(name)
        accept = '@'

    elif kind is inspect.Parameter.VAR_POSITIONAL:
        args.append(name)
        kwargs['nargs'] = '*'
        accept = '*'
    elif kind is inspect.Parameter.KEYWORD_ONLY:
        args.append('--' + name)
        accept = '='
    elif kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:
        if default:
            args.append('--' + name)
            accept = '='
        else:
            args.append(name)
            accept = '@'
    elif kind is inspect.Parameter.VAR_KEYWORD:
        raise NotImplemented

    return name, accept, args, kwargs


def wise(fn: types.FunctionType):
    sig = inspect.Signature.from_callable(fn)
    parser = argparse.ArgumentParser(
        prog=LightBlue(fn.__name__),
        description=Green(fn.__doc__),
        add_help=True)
    actions = []
    for name, accept, args, kwargs in map(_describe_parameter,
                                          sig.parameters.values()):
        actions.append((name, accept))
        parser.add_argument(*args, **kwargs)

    def parse_arg(argv):
        if not argv:
            parser.print_help()
            return 0
        cmd_args = parser.parse_args(argv)
        args = []
        kwargs = {}
        for name, accept in actions:
            arg = getattr(cmd_args, name)
            if accept == '=':
                kwargs[name] = arg
            elif accept == '*':
                args.extend(arg)
            elif accept == '@':
                args.append(arg)
        return fn(*args, **kwargs)

    return parse_arg
