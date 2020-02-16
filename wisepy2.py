import inspect
import types
import argparse
from argparse import RawTextHelpFormatter

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
        strings = map(lambda each: '{}{}'.format(colored, each), strings)
        return '{}{}'.format(sep.join(strings), _Colored.Clear)

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
    store_bool = False

    if anno:
        if anno is bool and isinstance(default, bool):
            store_bool = True
            kwargs['action'] = 'store_false' if default else 'store_true'
        elif isinstance(anno, type):
            kwargs['type'] = anno
        kwargs['help'] = Blue(str(anno))

    if not store_bool and p.default is not inspect._empty:
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
        if p.default is not inspect._empty:
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
        add_help=True,
        formatter_class=RawTextHelpFormatter)
    actions = []
    for name, accept, args, kwargs in map(_describe_parameter,
                                          sig.parameters.values()):
        actions.append((name, accept))
        parser.add_argument(*args, **kwargs)

    def parse_arg(argv=None):
        if argv:
            cmd_args = parser.parse_args(argv)
        else:
            cmd_args = parser.parse_args()
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
