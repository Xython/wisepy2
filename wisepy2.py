import inspect
import types
import argparse
import typing
from abc import ABC, abstractmethod

__all__ = ["wise"]


def _prepare_type_hints(f):
    if hasattr(typing, "get_type_hints"):
        f.__annotations__ = typing.get_type_hints(f)


def process_empty(x):
    if x is inspect._empty:
        return None
    return x


class _Colored:
    Red = "\033[31m"
    Green = "\033[32m"
    Yellow = "\033[33m"
    Blue = "\033[34m"
    Purple = "\033[35m"
    LightBlue = "\033[36m"
    Clear = "\033[39m"
    Purple2 = "\033[95m"


def _wrap_color(colored: str):
    def func(*strings: str, sep=""):
        strings = map(lambda each: "{}{}".format(colored, each), strings)  # type: ignore
        return "{}{}".format(sep.join(strings), _Colored.Clear)

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
    """The formatter is from https://github.com/vanyakosmos/argser"""

    def __init__(self, prog, indent_increment=4, max_help_position=32, width=120):
        super().__init__(prog, indent_increment, max_help_position, width)

    def start_section(self, heading):
        heading = HEAD_COLOR(heading)
        return super().start_section(heading)

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = USAGE_COLOR("usage") + ": "
        return super().add_usage(usage, actions, groups, prefix)

    def _get_type(self, action):
        meta = getattr(action, "__meta", None)
        if not meta:
            return
        if isinstance(meta.type, type):
            typ = getattr(meta.type, "__name__", "-")
        else:
            typ = str(meta.type)
            typ = typ.replace("typing.", "")  # typing.List[str] -> List[str]
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


def _describe_parameter(
    p: inspect.Parameter, hints: dict, parser: argparse.ArgumentParser
):
    kind = p.kind
    name = p.name
    anno = hints.get(name)
    default = process_empty(p.default)

    common_kwargs = {}
    if anno is not None:
        common_kwargs["help"] = Blue(str(anno))

    if anno and anno is bool and isinstance(default, bool):
        kwargs = common_kwargs.copy()
        kwargs["action"] = "store_false" if default else "store_true"
        parser.add_argument("--" + name, **kwargs)
        return "="

    if isinstance(anno, type):
        common_kwargs["type"] = anno

    if p.default is not inspect._empty:
        common_kwargs["default"] = default

    if kind is inspect.Parameter.POSITIONAL_ONLY:
        parser.add_argument(name, **common_kwargs)

        return "@"

    elif kind is inspect.Parameter.VAR_POSITIONAL:

        parser.add_argument(name, nargs="*", **common_kwargs)
        return "*"

    elif kind is inspect.Parameter.KEYWORD_ONLY:
        kwargs = common_kwargs.copy()
        kwargs["required"] = p.default is inspect._empty
        parser.add_argument("--" + name, **kwargs)
        return "="

    elif kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:

        pos_kwargs = common_kwargs.copy()
        pos_kwargs["nargs"] = "?"
        pos_kwargs["metavar"] = name
        t = typing.cast(type, pos_kwargs.get("type", str))
        pos_kwargs["type"] = str
        pos_kwargs["default"] = argparse.SUPPRESS
        parser.add_argument(name, **pos_kwargs)

        kw_kwargs = common_kwargs.copy()
        parser.add_argument("--" + name, **kw_kwargs)
        return t
    else:
        raise NotImplementedError("unknown kind {}".format(kind))


class CommandConstruction(ABC):
    @abstractmethod
    def construct(self, prog: str, description: str):
        raise NotImplementedError


class MainConstruction(CommandConstruction):
    def __init__(self):
        self.parser: "argparse.ArgumentParser" = None  # type: ignore

    def construct(self, prog: str, description: str):
        self.parser = argparse.ArgumentParser(
            prog=prog,
            description=Green(description),
            add_help=True,
            formatter_class=HelpFormatter,
        )
        return self.parser


class SubConstruction(CommandConstruction):
    def __init__(self, sub_parsers: "argparse._SubParsersAction"):
        self.sub_parsers = sub_parsers

    def construct(self, prog: str, description: str):
        p = self.sub_parsers.add_parser(
            name=prog, prog=prog, add_help=True, description=Green(description)
        )
        return p


def _wise_wrap_class(cls: type, ctor: CommandConstruction):
    parser = ctor.construct(prog=cls.__name__, description=cls.__doc__ or "")
    dest = "SUB-OF " + cls.__name__
    subparsers: "argparse._SubParsersAction" = parser.add_subparsers(dest=dest)
    parser_funcs = {}
    for field, value in cls.__dict__.items():
        if not field.startswith("__"):
            if isinstance(value, staticmethod) and isinstance(
                value.__func__, types.FunctionType
            ):
                parser_funcs[field] = _wise_wrap_func(
                    value.__func__, SubConstruction(subparsers)
                )
            elif isinstance(value, type):
                parser_funcs[field] = _wise_wrap_class(
                    value, SubConstruction(subparsers)
                )

    def parse_arg(cmd_args: argparse.Namespace):
        field = getattr(cmd_args, dest, None)
        if field:
            return parser_funcs[field](cmd_args)

    return parse_arg


def _wise_wrap_func(fn: types.FunctionType, ctor: CommandConstruction):
    _prepare_type_hints(fn)
    sig = inspect.Signature.from_callable(fn)
    parser: "argparse.ArgumentParser" = ctor.construct(
        prog=fn.__name__, description=fn.__doc__ or ""
    )
    actions = []
    hints = getattr(fn, "__annotations__", {})
    for p in sig.parameters.values():
        accept = _describe_parameter(p, hints, parser)
        actions.append((p.name, accept))

    def parse_arg(cmd_args: argparse.Namespace):
        args = []
        kwargs = {}
        for name, accept in actions:
            arg = getattr(cmd_args, name)
            if accept == "=":
                arg = getattr(cmd_args, name)
                kwargs[name] = arg
            elif accept == "*":
                arg = getattr(cmd_args, name)
                args.extend(arg)
            elif accept == "@":
                arg = getattr(cmd_args, name)
                args.append(arg)
            else:
                if not isinstance(arg, accept):
                    try:
                        arg = accept(arg)
                    except:
                        import sys

                        sys.exit(
                            Red(
                                "error: argument --{} should be {}, but got {}".format(
                                    name, accept, arg
                                )
                            )
                        )
                kwargs[name] = arg
        return fn(*args, **kwargs)

    return parse_arg


def _wise_impl(fn):
    """convert a Python function into a command line"""
    main_construction = MainConstruction()
    if isinstance(fn, type):
        handle = _wise_wrap_class(fn, main_construction)
    elif isinstance(fn, types.FunctionType):
        _prepare_type_hints(fn)
        handle = _wise_wrap_func(fn, main_construction)
    else:
        raise TypeError(type(fn))

    parser = main_construction.parser

    def parse_arg(argv=None):
        if argv is not None:
            assert isinstance(argv, list), (
                "a str input is not supported!"
                "Transform your input to a correct list using `import shlex;shlex.split(string_argv)`"
            )
            cmd_args = parser.parse_args(argv)
        else:
            cmd_args = parser.parse_args()
        return handle(cmd_args)

    return parse_arg


if typing.TYPE_CHECKING:
    R_co = typing.TypeVar("R_co", covariant=True)

    class _ArgumentProcessor(typing.Protocol[R_co]):
        def __call__(self, args: list[str] | None = None) -> R_co:
            ...

    R = typing.TypeVar("R")

    def wise(f: typing.Callable[..., R]) -> _ArgumentProcessor[R]:
        """convert a Python function into a command line"""
        ...

else:
    wise = _wise_impl
