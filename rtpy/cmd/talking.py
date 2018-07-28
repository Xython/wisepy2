from functools import reduce

import typing

from rtpy.cmd.fn_describe import describe
from rtpy.cmd.dynamic_cast import dynamic_cast
from rtpy.cmd.cmd_parser import parse
from rtpy.cmd.cmd_ast import Quote, Cmd, Pipeline
from rtpy.cmd.color import Red, Green, Blue, Yellow, Purple, LightBlue
import readline
import types
import io
from Redy.Tools.PathLib import Path
from pprint import pprint


# TODO: remove this Pipe class. it's not a good abstraction.
class Pipe:
    empty: 'Pipe'

    def __init__(self, com, call):
        self.com: Component = com
        self.call = call

    def display(self):
        self.com.display(self.call(None))

    def get(self, arg=None):
        return self.call(arg)


Pipe.empty = Pipe(None, lambda this: ())


class Component:
    def __init__(self, fn, name, help_doc):
        self.fn: types.FunctionType = fn  # original function
        self.name: str = name  # command name
        self.help_doc = help_doc
        self._complete = None
        self._display = None

    def __call__(self, *args, **kwargs):
        return dynamic_cast(self.fn)(*args, **kwargs)

    def completer(self, func):
        self._complete = func
        return self

    def displayer(self, func):
        self._display = func
        return self

    def complete(self, partial):
        if self._complete:
            return self._complete(partial)
        return ()

    def display(self, result):
        if not self._display:
            if isinstance(result, (list, tuple, dict)):
                pprint(result)
            elif result is not None:
                print(result)
            return
        self._display(result)


def _generate_options(_registered_cmds: dict, partial: str, state: int):
    line = readline.get_line_buffer()
    option: Component = next((com for cmd_name, com in _registered_cmds.items() if line.startswith(cmd_name)), None)
    if option:
        ret = option.complete(line)
        return ret

    return (each for each in _registered_cmds if each.startswith(partial))


class Talking:

    def __init__(self):
        self._registered_cmds = {}

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

    def completer(self, partial: str, state):
        options = tuple(option for option in _generate_options(self._registered_cmds, partial, state) if
                        option.startswith(partial))

        if state < len(options):
            return options[state]
        else:
            state -= 1

    def process(self, inp):
        if isinstance(inp, Pipeline):
            return self.process_pipeline(inp)
        elif isinstance(inp, Cmd):
            return self.process_cmd(inp)
        raise TypeError(type(inp))

    def process_pipeline(self, pipeline: Pipeline) -> Pipe:
        piped = Pipe.empty

        # assert len(pipeline.cmds) > 1

        def _reduce(_pipe, _piped):
            return lambda _: _pipe.get(_piped.get())(_pipe, _piped)

        for each in pipeline.cmds:
            pipe = self.process(each)
            piped = Pipe(pipe.com, _reduce(pipe, piped))

        return piped

    def process_cmd(self, command: Cmd) -> Pipe:
        instruction, args, kwargs = command.inst, command.args, command.kwargs
        instruction = self.visit_arg(instruction)

        com: Component = self._registered_cmds.get(instruction)

        if not com:
            raise ValueError(f'No function registered/aliased as `{instruction}`.', UserWarning)

        if kwargs and any(True for k, _ in kwargs if k == 'help'):
            return Pipe(com, lambda this: com.help_doc)

        args = map(self.visit_arg, args) if args else ()
        kwargs = {k: v for k, v in kwargs} if kwargs else {}

        try:
            return Pipe(com, lambda this: com(this, *args, **kwargs) if this else com(*args, **kwargs))
        except Exception as e:
            print(com.help_doc)
            raise e

    def visit_arg(self, pat):
        if isinstance(pat, Quote):
            pat = pat.cmd

            if isinstance(pat, Cmd):
                return self.process_cmd(pat).get()

            elif isinstance(pat, Pipeline):
                return self.process_pipeline(pat).get()

            else:
                raise TypeError(type(pat))

        if isinstance(pat, str):
            return pat

    def from_io(self, ios: io.BufferedReader):
        self.process(parse(ios.read())).display()

    def from_text(self, text):
        self.process(parse(text)).display()

    def listen(self):
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.completer)
        readline.set_completer_delims(' \t\n;/')
        while True:
            print('wd: ', Green(Path('.')))

            cmd = input('rush> ')

            if cmd == 'exit':

                break

            self.from_text(cmd)
