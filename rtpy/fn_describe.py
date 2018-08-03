import inspect
import types
import io
import textwrap

arg_description = {
    inspect.Parameter.KEYWORD_ONLY: 'keyword only',
    inspect.Parameter.POSITIONAL_ONLY: 'positional only',
    inspect.Parameter.VAR_KEYWORD: '**kwargs',
    inspect.Parameter.VAR_POSITIONAL: '*args',
    inspect.Parameter.POSITIONAL_OR_KEYWORD: 'positional or keyword arg'
}


def _fst(x: tuple):
    return x[0]


def _transac(predicate):
    def _inner(it: object, if_not_so, if_so=None):
        if predicate(it):
            return if_so
        return if_not_so(it)

    return _inner


_empty_transac = _transac(lambda _: _ is inspect._empty)


def _describe_parameter(param: inspect.Parameter):
    kind = arg_description[param.kind]

    description: str = _empty_transac(param.annotation, if_not_so=str)

    param_head = f"- {param.name}({kind})"

    if param.default is not inspect._empty:
        param_head += f' = {param.default!r}'

    if description:
        if description.count('\n'):
            description = '\n' + textwrap.indent(description,
                                                 ' ' * len(param_head))
        else:
            description = description

    return param_head, description


def describe(fn: types.FunctionType, alias=None):
    sig = inspect.Signature.from_callable(fn)
    fn_name = alias or fn.__name__
    params = sig.parameters

    with io.StringIO() as ios:
        ios.write(fn_name + '\t')
        if fn.__doc__:
            ios.write(fn.__doc__ + '\n')
        param_info_lst = [
            _describe_parameter(each) for each in params.values()
        ]
        if param_info_lst:
            max_param_head_length = max(
                map(lambda _: len(_fst(_)), param_info_lst))
            for param_head, description in param_info_lst:
                ios.write(param_head)
                ios.write(' ' * (max_param_head_length - len(param_head)))

                if description:
                    ios.write(' : ')
                    ios.write(description)
                ios.write('\n')

        return textwrap.indent(ios.getvalue(), '  ')
