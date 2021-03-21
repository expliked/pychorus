"""
A Python library for the chorus.fightthe.pw site.

This uses the website's API but transforms it into a Python-enviorment.
"""
from .pychorus import *

__all__ = [
    "Song",
    "search",
    "latest",
    "random",
    "count",
    "SongNotFoundError",
    "PageNotFoundError"
]

__version__ = "0.023"
__author__ = "expliked"
