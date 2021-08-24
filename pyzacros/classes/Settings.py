"""
Module containing the Settings class.
"""

import scm.plams

import textwrap
import contextlib
from functools import wraps

__all__ = ['Settings']

class Settings( scm.plams.Settings ):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
