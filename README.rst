.. image:: https://img.shields.io/pypi/v/wisepy2.svg
    :target: https://pypi.python.org/pypi/wisepy2

Wisepy2
==================

Since we found that the capabilities/features doesn't attract people into using [wisepy](https://github.com/Xython/wisepy), thus
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