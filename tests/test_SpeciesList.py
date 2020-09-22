#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

from pyzacros.classes.Species import Species
from pyzacros.classes.SpeciesList import SpeciesList
from pyzacros.utils.compareReports import *


def test_SpeciesList():
    """Test of the SpeciesList class."""
    print( "---------------------------------------------------" )
    print( ">>> Testing SpeciesList class" )
    print( "---------------------------------------------------" )

    # Adsorbed specie
    myAdsorbedSpecies1 = Species( "H2*", denticity=1 )
    myAdsorbedSpecies2 = Species( "O2*", denticity=1 )

    # Gas specie
    myGasSpecies1 = Species( "H2", gas_energy=0.0 )

    # Gas specie
    myGasSpecies2 = Species( "O2", gas_energy=0.0 )

    # Free adsorption site
    myFreeAdsorptionSite = Species( "*" )

    mySpeciesList = SpeciesList()
    mySpeciesList.append( myAdsorbedSpecies1 )
    mySpeciesList.append( myAdsorbedSpecies2 )
    mySpeciesList.append( myGasSpecies1 )
    mySpeciesList.append( myGasSpecies2 )
    mySpeciesList.append( myFreeAdsorptionSite )

    print(mySpeciesList)

    output = str(mySpeciesList)
    expectedOutput = """\
n_gas_species 2
gas_specs_names           H2        O2
gas_energies             0.0       0.0
gas_molec_weights     2.0156   31.9898
n_surf_species 2
surf_specs_names         H2*       O2*
surf_specs_dent            1         1\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )
