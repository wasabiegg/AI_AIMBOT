from __future__ import print_function

# from functools import wrap
# from typing import Callable
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def custom_assert(exp: bool, msg: str = ""):
    try:
        assert exp is True
    except AssertionError:
        eprint(msg)
        sys.exit(1)
