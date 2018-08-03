RTPY
====

RTPY is an intuitive and effective CLI framework which is scalable and
practical.

The most common use case might be an alternative of Python's
``argparser``, also you can enrich your terminal commands by using
``rtpy``.

The terminal utilities have been removed from ``rtpy``. One project, one
goal.

Install
-------

::

    pip install -U Redy rbnf rtpy

Usage
-----

.. code:: python


    from rtpy.talking import Talking
    talking = Talking()

    @talking
    def add(left: 'an integer', right: 'another integer'):
        """
        add up two numbers.
        """
        left = int(left)
        right = int(right)
        return left + right

    if __name__ == '__main__':
        talking.on()

And then use this python script:

.. code:: shell

    cmd> python add --help # not only `cmd`, support all terminal as well.

      add
          add up two numbers.

      - left(positional or keyword arg)  : an integer
      - right(positional or keyword arg) : another integer

    cmd> python demo.py add 1 2

    3

Another example here shows that ``rtpy`` can translate python functions
with any kinds of parameter signatures into terminal command.

.. code:: python

    @talking.alias('sum')
    def another(*args,
                to_float: bool = False,
                double=None,
                additional_add: int = None):
        """
        my sum command
        """

        # using type annotation in keyword argument makes the argument
        # cast to the specific type.

        ret = sum(map(int, args))

        if double:
            ret = ret * 2

        if to_float:
            ret = float(ret)

        if additional_add:
            ret += additional_add

        return ret

See terminal:

.. code:: shell

    cmd> python demo.py sum --help

      sum
          my sum command

      - args(*args)
      - to_float(keyword only) = False      : <class 'bool'>
      - double(keyword only) = None
      - additional_add(keyword only) = None : <class 'int'>

    cmd> python demo.py sum 1 2 3

    6

    cmd> python demo.py sum 1 2 3 --double

    12

    cmd> python demo.py sum 1 2 3 -additional_add 5 --double --to_float

    17.0
