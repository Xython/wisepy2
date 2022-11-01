import argparse
from ast import parse
from wisepy2 import wise

p1 = argparse.ArgumentParser()
p1.add_subparsers()


@wise
class Main:
    """
    abc de asdasdsa asdaadas
    asdsa sfadgx  shfxssareijap
    t rojifa erhgiasipgupw
    """

    @staticmethod
    def add(a: int, b: float):
        """
        add help doc: blah
        """
        print(a + b)

    @staticmethod
    def mul(a: int, b: int):
        """
        mul help doc: blah
        """
        print(a * b)

    class String:
        @staticmethod
        def concat(a: str, b: str):
            """
            string concat
            """
            return a + b

        @staticmethod
        def repeat(a: str, i: int):
            """
            string repeat
            """
            return a * i


print(Main())
