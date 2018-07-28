import typing


class Cmd(typing.NamedTuple):
    inst: str
    args: typing.Optional[typing.List[str]]
    kwargs: typing.Optional[typing.List[typing.Tuple[str, typing.Union[str, 'Quote']]]]


class Quote(typing.NamedTuple):
    cmd: Cmd


class Last(typing.NamedTuple):
    num: int


class Pipeline(typing.NamedTuple):
    cmds: typing.Tuple[Cmd, ...]
