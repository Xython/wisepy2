
RTPY
====================

RTPY is an intuitive and effective CLI framework which is scalable and practical.

The most common use case might be an alternative of Python's `argparser`,
however it's so easy for RTPY user to extend shell commands.(**For example, I just implemented
`autojump` in 2 hours and a half. I spent so long for I'm so sleepy in the mid-night :)**)

As New Argument Parser
----------------------------------


```python

from rtpy.cmd.talking import Talking

talking = Talking()


@talking
def add(left, right):
    left = int(left)
    right = int(right)
    return left + right


if __name__ == '__main__':
    import sys

    talking.from_text(' '.join(sys.argv[1:]))
```
And then use this python script:

```shell
cmd> python add --help # not only `cmd`, support all terminal as well.

add
- left(positional or keyword arg)
- right(positional or keyword arg)

cmd> python demo.py add 1 2

3
```

Another example here shows that `rtpy` can translate python functions with
any kinds of parameter signatures into terminal command.

```python
@talking.alias('sum')
def another(*args, to_float: bool = False, double=None, additional_add: int = None):

    # using type annotation in keyword argument makes the argument
    # cast to the specific type.

    ret = sum(map(int, args))

    if double:
        ret = ret * 2

    if to_float:
        ret = float(ret)

    if additional_add:
        ret += eval(additional_add)

    return ret
```

See terminal:

```shell
cmd> python demo.py sum --help

sum
- args(*args)
- to_float(keyword only) = False      : <class 'bool'>
- double(keyword only) = None
- additional_add(keyword only) = None : specify some number to accumulate with at the final result

cmd> python demo.py sum 1 2 3

6

cmd> python demo.py sum 1 2 3 --double

12

cmd> python demo.py sum 1 2 3 --double --to_float --additional_add 5

17.0
```


Fast Terminal
------------------------

You can see the codes at `rtpy/_terminal`, I have just implemented full featured `ls`, `cd`, `echo`, pipe-operator and quote expression.


[![terminal_demo](https://github.com/thautwarm/rtpy/blob/master/terminal_demo.jpg)](https://github.com/thautwarm/rtpy/blob/master/terminal_demo.jpg)

The implementations are so trivial:

See `rtpy.terminal.path`:

```python

@talking
def ls(suffix: ' a filename suffix to apply filtering. default to perform no filtering.' = None, *,
       r: 'is recursive' = False):
    filter_fn = None
    app = Path.collect if r else Path.list_dir

    if suffix:
        def filter_fn(_: str):
            return _.endswith(suffix)
    listed = [str(each) for each in app(Path('.'), filter_fn)]
    return listed

@talking
def cd(pattern: str):
    return os.chdir(str(Path(pattern)))

```

And `autojump` is very easy to implement, too.


- Auto Jump

    See [autojump in rtpy-terminal](https://github.com/thautwarm/rtpy/blob/master/rtpy/rtpy-terminal/path.py).

[![autojump](https://github.com/thautwarm/rtpy/blob/master/auto_jump.jpg)](https://github.com/thautwarm/rtpy/blob/master/auto_jump.jpg)


Contribute
-------------------

Welcome to

- Report issues about API/Plugin System designing.

- Make interesting and powerful commands to `rbnf/_terminal`.






