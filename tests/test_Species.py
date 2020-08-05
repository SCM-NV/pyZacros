#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

from pyzacros.classes.Species import Species
from pyzacros.classes.Cluster import Cluster


def test_Species():
    """Test of the Species class."""
    print("---------------------------------------------------")
    print(">>> Testing Species class")
    print("---------------------------------------------------")

    # Adsorbed specie
    myAdsorbedSpecies = Species("H2*", denticity=1)
    print(myAdsorbedSpecies)

    output = str(myAdsorbedSpecies)
    expectedOutput = "H2*"
    assert(output == expectedOutput)

    # Gas specie
    myGasSpecies = Species("H2", gas_energy=0.0)
    print(myGasSpecies)

    output = str(myGasSpecies)
    expectedOutput = "H2"
    assert(output == expectedOutput)

    # Free adsorption site
    myAdsorptionFreeSite = Species("*")
    print(myAdsorptionFreeSite)

    output = str(myAdsorptionFreeSite)
    expectedOutput = "*"
    assert(output == expectedOutput)
