from rbnf.core.State import State
import rbnf.zero as ze

try:
    from rtpy._cmd_parser import ulang
except:
    from Redy.Tools.PathLib import Path

    ze_exp = ze.compile("""
    
import  std.common.[Space DoubleQuotedStr Str]
[python] import rtpy.cmd_ast.[*]
ignore [Space Newline]

arg     ::= Str as str | DoubleQuotedStr as str | pattern as pat | quote as expr | closure as expr | placeholder as expr
            rewrite
                if expr:
                    return expr
                
                if str:
                    return eval(str.value)
                
                pat.value

placeholder ::= '$' arg as arg
                rewrite 
                    PlaceHolder(arg)

quote   ::= '`' command as cmd '`'
            rewrite
                Quote(cmd)
                
flag ::= '--' pattern as key
            with 
                key.value.isidentifier()
            rewrite
                (key.value, True)
                
must     ::= '-' pattern as key arg as value
            with 
                key.value.isidentifier()
            rewrite
                (key.value, value)

closure ::= '{' [command to [stmts] (';' command to [stmts])*] [';'] '}' 
            rewrite Closure(stmts)
                
command ::= arg as instruction (  (arg  as last) to [args] 
                                | (flag as last) to [kwargs] 
                                | (must as last) to [kwargs]
                                )* 
                                ['|' command as and_then]
            rewrite
                while isinstance(last, Cmd) and isinstance(last.last, Cmd):
                    last = last.last
                 
                ret = Cmd(instruction, args, kwargs, last)
                
                if and_then:                    
                    args = and_then.args or ()
                    ret = Cmd(and_then.inst, (ret, *args), and_then.kwargs, and_then.last)
                
                ret
                    
pattern := R'[^`\s\{\}\;]+'
Newline := '\n'

""")

    with Path(__file__).parent().into('_cmd_parser.py').open('w') as file_io:
        file_io.write(ze_exp._lang.dumps())

    from rtpy._cmd_parser import ulang

from rbnf.edsl.rbnf_analyze import check_parsing_complete
_command = ulang.named_parsers['command']
_impl = ulang.implementation


def parse(text: str, strict_match=False) -> ze.ResultDescription:
    tokens = tuple(ulang.lexer(text))

    state = State(_impl, filename='<rush>')

    result = _command.match(tokens, state)

    if not strict_match:
        check_parsing_complete(text, tokens, state)

    return ze.ResultDescription(state, result, tokens)
