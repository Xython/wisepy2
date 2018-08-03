import typing as t

Arg = t.Union[str, 'Quote']


class Cmd(t.NamedTuple):
    inst: Arg
    args: t.Optional[t.List[Arg]]
    kwargs: t.Optional[t.List[t.Tuple[str, Arg]]]
    last: Arg


class Quote(t.NamedTuple):
    cmd: Cmd


class Closure(t.NamedTuple):
    stmts: t.List[Cmd]


class PlaceHolder(t.NamedTuple):
    value: t.Union[Quote]
