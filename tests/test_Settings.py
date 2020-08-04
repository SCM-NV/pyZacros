#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

from pyzacros.classes.Settings import Settings 


def test_Settings():
    """Test of the Settings class."""
    print("---------------------------------------------------")
    print(">>> Testing Settings class")
    print("---------------------------------------------------")

    # Adsorbed specie
    sett = Settings()
    sett.simulation_input.random_seed =71543
    sett.input.basis.type = 'TZ2P'
    sett.input.geometry.sp = True
    sett.input.xc.gga = 'PW91'
#    myAdsorbedSpecies = Species("H2*", denticity=1)
#   print(myAdsorbedSpecies)

#    output = str(myAdsorbedSpecies)
#    expectedOutput = "H2*"
#    assert(output == expectedOutput)
#
#    # Gas specie
#    myGasSpecies = Species("H2", gas_energy=0.0)
#    print(myGasSpecies)
#
#    output = str(myGasSpecies)
#    expectedOutput = "H2"
#    assert(output == expectedOutput)
#
#    # Free adsorption site
#    myAdsorptionFreeSite = Species("*")
#    print(myAdsorptionFreeSite)
#
#    output = str(myAdsorptionFreeSite)
#    expectedOutput = "*"
#    assert(output == expectedOutput)
#