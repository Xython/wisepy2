from rbnf.State import State
from rbnf.Color import Red, Green

try:
    from ._cmd_parser import ulang
except:
    from Redy.Tools.PathLib import Path
    import rbnf.zero as ze

    ze_exp = ze.compile("""
import  std.common.[Space DoubleQuotedStr Str]
[python] import rtpy.cmd.cmd_ast.[*]
ignore [Space]


arg     ::= Str as str | DoubleQuotedStr as str | pattern as pat | quote as quote 
            rewrite
                if str:
                    return eval(str.value)
                if quote:
                    return quote
                pat.value

quote   ::= '`' command as cmd '`'
            rewrite
                Quote(cmd)
                
keyword ::= '--' pattern as key [arg as value]
            with 
                key.value.isidentifier()
            rewrite
                (key.value, value or True)


command ::= arg as instruction (arg to [args] | keyword to [kwargs])* ('|' command to [and_then])*
            rewrite
                ret = Cmd(instruction, args, kwargs)
                if and_then:
                    ret = Pipeline((ret, *and_then))
                ret
                    
pattern := R'[^`\s]+'
    """)

    with Path(__file__).parent().into('_cmd_parser.py').open('w') as file_io:
        file_io.writeline(ze_exp._lang.dumps())

    from ._cmd_parser import ulang

from rbnf.edsl.rbnf_analyze import check_parsing_complete

_command = ulang.named_parsers['command']
_impl = ulang.implementation


def parse(text: str):
    tokens = tuple(ulang.lexer(text))
    state = State(_impl)
    result = _command.match(tokens, state)
    check_parsing_complete(text, tokens, state)
    return result.value
