import inspect
import types
import argparse
import typing
from abc import ABC, abstractmethod

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
        strings = map(lambda each: '{}{}'.format(colored, each), strings) # type: ignore
        return '{}{}'.format(sep.join(strings), _Colored.Clear)

    return func


Red = _wrap_color(_Colored.Red)
Green = _wrap_color(_Colored.Green)
Yellow = _wrap_color(_Colored.Yellow)
Blue = _wrap_color(_Colored.Blue)
Purple = _wrap_color(_Colored.Purple)
LightBlue = _wrap_color(_Colored.LightBlue)
Purple2 = _wrap_color(_Colored.Purple2)


HEAD_COLOR = Purple2
USAGE_COLOR = Yellow
TYPE_COLOR = Blue
DEFAULT_COLOR = Green
INVOC_COLOR = LightBlue

class HelpFormatter(argparse.RawTextHelpFormatter):
    """The formatter is from https://github.com/vanyakosmos/argser
    """

    def __init__(self, prog, indent_increment=4, max_help_position=32, width=120):
        super().__init__(prog, indent_increment, max_help_position, width)

    def start_section(self, heading):
        heading = HEAD_COLOR(heading)
        return super().start_section(heading)

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = USAGE_COLOR('usage') + ': '
        return super().add_usage(usage, actions, groups, prefix)

    def _get_type(self, action):
        meta = getattr(action, '__meta', None)
        if not meta:
            return
        if isinstance(meta.type, type):
            typ = getattr(meta.type, '__name__', '-')
        else:
            typ = str(meta.type)
            typ = typ.replace('typing.', '')  # typing.List[str] -> List[str]
        return str(typ)

    def format_default_help(self, action):
        # skip if current action is sub-parser
        if action.nargs == argparse.PARSER:
            return
        typ = self._get_type(action)
        if not typ:
            return
        typ = TYPE_COLOR(typ)
        default = DEFAULT_COLOR(repr(action.default))
        res = str(typ)
        if action.option_strings or action.default is not None:
            res += f", default: {default}"
        return res

    def format_action_help(self, action):
        if action.default == argparse.SUPPRESS:
            return action.help
        default_help_text = self.format_default_help(action)
        if default_help_text:
            if action.help:
                return f"{default_help_text}. {action.help}"
            return default_help_text
        return action.help

    def _format_action(self, action):
        action.help = self.format_action_help(action)
        # noinspection PyProtectedMember
        text = super()._format_action(action)
        invoc = self._format_action_invocation(action)
        s = len(invoc) + self._current_indent
        text = LightBlue(text[:s]) + text[s:]
        return text


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
            anno = "bool"
        elif isinstance(anno, type):
            kwargs['type'] = anno
            anno = anno.__name__
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


class CommandConstruction(ABC):
    @abstractmethod
    def construct(self, prog: str, description: str):
        raise NotImplementedError


class MainConstruction(CommandConstruction):
    def __init__(self):
        self.parser: 'argparse.ArgumentParser' = None  # type: ignore

    def construct(self, prog: str, description: str):
        self.parser = argparse.ArgumentParser(
            prog=prog,
            description=Green(description),
            add_help=True,
            formatter_class=HelpFormatter
        )
        return self.parser


class SubConstruction(CommandConstruction):
    def __init__(self, sub_parsers: 'argparse._SubParsersAction'):
        self.sub_parsers = sub_parsers

    def construct(self, prog: str, description: str):
        p = self.sub_parsers.add_parser(
            name=prog,
            prog=prog,
            add_help=True,
            description=Green(description)
        )
        return p


def _wise_wrap_class(cls: type, ctor: CommandConstruction):
    parser = ctor.construct(
        prog=cls.__name__,
        description=cls.__doc__ or ""
    )
    dest = "SUB-OF " + cls.__name__
    subparsers: 'argparse._SubParsersAction' = parser.add_subparsers(dest=dest)
    parser_funcs = {}
    for field, value in cls.__dict__.items():
        if not field.startswith('__'):
            if isinstance(value, staticmethod) and isinstance(value.__func__, types.FunctionType):
                parser_funcs[field] = _wise_wrap_func(
                    value.__func__, SubConstruction(subparsers))
            elif isinstance(value, type):
                parser_funcs[field] = _wise_wrap_class(
                    value, SubConstruction(subparsers))

    def parse_arg(cmd_args: argparse.Namespace):
        field = getattr(cmd_args, dest, None)
        if field:
            return parser_funcs[field](cmd_args)

    return parse_arg


def _wise_wrap_func(fn: types.FunctionType, ctor: CommandConstruction):
    sig = inspect.Signature.from_callable(fn)
    parser: 'argparse.ArgumentParser' = ctor.construct(
        prog=fn.__name__,
        description=fn.__doc__ or "")
    actions = []
    for name, accept, args, kwargs in map(_describe_parameter,
                                          sig.parameters.values()):
        actions.append((name, accept))
        parser.add_argument(*args, **kwargs)

    def parse_arg(cmd_args: argparse.Namespace):
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


def _wise_impl(fn):
    """convert a Python function into a command line
    """
    main_construction = MainConstruction()
    if isinstance(fn, type):
        handle = _wise_wrap_class(fn, main_construction)
    elif isinstance(fn, types.FunctionType):
        handle = _wise_wrap_func(fn, main_construction)
    else:
        raise TypeError(type(fn))

    parser = main_construction.parser

    def parse_arg(argv=None):
        if argv:
            cmd_args = parser.parse_args(argv)
        else:
            cmd_args = parser.parse_args()
        return handle(cmd_args)
    return parse_arg


if typing.TYPE_CHECKING:
    def wise(x):
        """convert a Python function into a command line
        """
        return x
else:
    wise = _wise_impl
