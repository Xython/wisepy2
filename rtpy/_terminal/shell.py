from . import talking
from subprocess import PIPE, Popen


@talking.alias(':')
def call_system(*pattern):
    """
    this supplies a way to call builtin terminal commands.
    """

    p = Popen(' '.join(map(str, pattern)), stdout=PIPE, shell=True)
    res, err = p.communicate()
    return res.decode()
