#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the pyZacros module.
"""
import pytest
import sys

from pyzacros.classes.kmc import KmcSimulation
from pyzacros.classes.Species import Species
from pyzacros.classes.SpeciesList import SpeciesList
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.Mechanism import Mechanism

"""
Tests on classes.
"""

Species.test()
SpeciesList.test()
Cluster.test()
ElementaryReaction.test()
Mechanism.test()


def test_with_error():
    with pytest.raises(ValueError):
        # Do something that raises a ValueError
        raise(ValueError)


# Fixture example
@pytest.fixture
def an_object():
    return {}


def test_pyZacros(an_object):
    assert an_object == {}
