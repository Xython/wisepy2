.. image:: https://img.shields.io/pypi/v/wisepy2.svg
    :target: https://pypi.python.org/pypi/wisepy2

Wisepy2
==================

Since we found that the capabilities/features doesn't attract people into using `wisepy <https://github.com/Xython/wisepy>`_, thus
we go to an extreme, making the simplest command line tool for Python, but also capable of covering the regular use cases.

Two examples are given in the root directory of this project.


.. image:: https://raw.githubusercontent.com/Xython/wisepy2/master/example-add2.png
    :width: 90%
    :align: center

.. code-block :: Python

    from wisepy2 import *
    import sys


    @wise
    def add(left: int, right: int):
        """
        add up two numbers.
        """
        print(left + right)
        return 0


    if __name__ == '__main__':
        add(sys.argv[1:])


Usage
=========================

Wisepy2 converts a function into a command line, where following components of python functions could correspond to
command line components. Here're the mapping rules:

- ``variadic args``: a positional argument that accepts variable number of arguments, like ``nargs="*"`` in ``argparse``.

- ``annotations``: an annotation will be transformed to the help doc of an argument. If it's a type, the argument is automatically converted to the type you expect.

- ``default argument``: default value will be equivalent to specifying ``default`` in ``argparse``.

- ``keyword argument``: keyword only or postional_or_keyword arguments with default values can be passed by ``--arg value``.

- arguments that're annotated ``bool`` and have ``True`` or ``False`` default arguments: these arguments can changed as the opposite of its default value by giving ``--arg``.


