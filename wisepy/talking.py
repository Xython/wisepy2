from wisepy.fn_describe import describe
from wisepy.dynamic_cast import dynamic_cast
from wisepy.cmd_parser import parse
from wisepy.cmd_ast import Quote, Cmd, Closure, PlaceHolder
from wisepy.color import *
from Redy.Magic.Pattern import Pattern
from pprint import pprint
import types
import io


class Component:
    def __init__(self, fn, name, help_doc):
        self.fn: types.FunctionType = fn  # original function
        self.name: str = name  # command name
        self.help_doc = help_doc
        self._display = None

    def __call__(self, *args, **kwargs):
        return dynamic_cast(self.fn)(*args, **kwargs)

    def displayer(self, func):
        """
        register a custom displayer to describe the command output.
        """
        self._display = func
        return self

    def display(self, result):

        if not self._display:
            if isinstance(result, (list, tuple, dict)):
                pprint(Blue(result))

            elif result is not None:
                print(result)

            return

        self._display(result)


class ShellFunction:
    def __init__(self, talking_session: 'Talking', stmts):

        self.talking_session = talking_session
        self.stmts = stmts

    def __call__(self, ctx: dict):

        talking_session = self.talking_session

        stmts = self.stmts

        if not stmts:
            return None

        *head, tail = stmts

        for each in head:
            talking_session.visit(each, ctx)

        return talking_session.visit(tail, ctx)

    def __repr__(self):
        return repr(self.stmts)


class Talking:
    def __init__(self):
        self._registered_cmds = {}
        self._current_com = None
        self._current_cmd = None

    @property
    def registered_cmds(self):
        return self._registered_cmds

    def __call__(self, func: types.FunctionType):
        return self.alias(func.__name__)(func)

    def alias(self, name):
        def _inner(func):
            com = Component(func, name, describe(func, name))
            self._registered_cmds[name] = com
            return com

        return _inner

    @Pattern
    def visit(self, ast, ctx):
        return type(ast)

    @visit.case(Quote)
    def visit_quote(self, ast: Quote, ctx: dict):
        return self.visit(ast.cmd, ctx)

    @visit.case(Closure)
    def visit_closure(self, ast: Closure, _):
        return ShellFunction(self, ast.stmts)

    @visit.case(PlaceHolder)
    def visit_place_holder(self, ast: PlaceHolder, ctx: dict):
        name = self.visit(ast.value, ctx)
        return ctx.get(name)

    @visit.case(str)
    def visit(self, ast: str, _):
        return ast

    @visit.case(Cmd)
    def visit(self, command: Cmd, ctx: dict):
        visit = self.visit
        instruction, args, kwargs = command.inst, command.args, command.kwargs
        instruction = visit(instruction, ctx)
        self._current_com = com = self._registered_cmds.get(instruction)

        if not com:
            raise ValueError(
                f'No function registered/aliased as `{instruction}`.')

        if kwargs and any(True for k, _ in kwargs if k == 'help'):
            return com.help_doc

        args = (visit(arg, ctx) for arg in args) if args else ()
        kwargs = {k: v for k, v in kwargs} if kwargs else {}

        try:
            return com(*args, **kwargs)
        except Exception as e:
            print(Purple2(com.help_doc))
            raise e

    def from_io(self, ios: io.TextIOWrapper, ctx: dict = None):
        ctx = ctx or {}
        result = self.visit(parse(ios.read()).result.value, ctx)
        self._current_com.display(result)

    def from_text(self, text, ctx: dict = None):
        ctx = ctx or {}
        result = self.visit(parse(text).result.value, ctx)
        self._current_com.display(result)

    def on(self):
        import sys
        recv = ' '.join(sys.argv[1:])
        stripped = recv.strip()
        if not stripped:
            print(
                Yellow(
                    "No command input, use --help to show available commands and their information."
                ))
        elif stripped == '--help':
            print(Blue("Available commands:"))
            for each in self._registered_cmds.values():
                print(Purple2(each.help_doc))

        else:
            self.from_text(recv, {})
        sys.exit(0)
