#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the pyZacros module."""

from pyzacros.classes.Species import Species
from pyzacros.classes.SpeciesList import SpeciesList
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.Mechanism import Mechanism


def test_classes():
    """Testing of classes."""
    Species.test()
    SpeciesList.test()
    Cluster.test()
    ElementaryReaction.test()
    Mechanism.test()
