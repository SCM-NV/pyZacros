"""
Module containing the Settings class.
"""

import scm.plams

__all__ = ['Settings']

class Settings( scm.plams.Settings ):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
