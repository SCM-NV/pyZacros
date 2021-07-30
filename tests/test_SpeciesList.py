#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import pyzacros as pz
from pyzacros.utils.compareReports import compare


def test_SpeciesList():
    """Test of the SpeciesList class."""
    print( "---------------------------------------------------" )
    print( ">>> Testing SpeciesList class" )
    print( "---------------------------------------------------" )

    # Adsorbed specie
    myAdsorbedSpecies1 = pz.Species( "H2*", denticity=1 )
    myAdsorbedSpecies2 = pz.Species( "O2*", denticity=1 )

    # Gas specie
    myGasSpecies1 = pz.Species( "H2", gas_energy=0.0 )

    # Gas specie
    myGasSpecies2 = pz.Species( "O2", gas_energy=0.0 )

    # Free adsorption site
    myFreeAdsorptionSite = pz.Species( "*" )

    #mySpeciesList = pz.SpeciesList()
    #mySpeciesList.append( myAdsorbedSpecies1 )
    #mySpeciesList.append( myAdsorbedSpecies2 )
    #mySpeciesList.append( myGasSpecies1 )
    #mySpeciesList.append( myGasSpecies2 )
    #mySpeciesList.append( myFreeAdsorptionSite )

    mySpeciesList = pz.SpeciesList( [myAdsorbedSpecies1,myAdsorbedSpecies2,myGasSpecies1,myGasSpecies2,myFreeAdsorptionSite] )

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
