#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import os
import time

import scm.plams

import pyzacros as pz
from pyzacros.utils.compareReports import compare

RUNDIR=None

def test_ZacrosJob_run():
    """Test of the ZacrosResults class."""
    global RUNDIR
    RUNDIR = os.getcwd()

    print( "---------------------------------------------------" )
    print( ">>> Testing ZacrosResults class" )
    print( "---------------------------------------------------" )

    scm.plams.init()

    #---------------------------------------------
    # Species:
    #---------------------------------------------
    # - Gas-species:
    CO_gas = pz.Species("CO")
    O2_gas = pz.Species("O2")
    CO2_gas = pz.Species("CO2", gas_energy=-2.337)

    # -) Surface species:
    s0 = pz.Species("*", 1)      # Empty adsorption site
    CO_ads = pz.Species("CO*", 1)
    O_ads = pz.Species("O*", 1)

    #---------------------------------------------
    # Lattice setup:
    #---------------------------------------------
    myLattice = pz.Lattice(lattice_type=pz.Lattice.RECTANGULAR, lattice_constant=1.0, repeat_cell=[20,20])

    #---------------------------------------------
    # Clusters:
    #---------------------------------------------
    CO_point = pz.Cluster(site_types=["1"], species=[CO_ads], cluster_energy=-1.3)
    O_point = pz.Cluster(site_types=["1"], species=[O_ads], cluster_energy=-2.3)

    #---------------------------------------------
    # Elementary Reactions
    #---------------------------------------------
    # CO_adsorption:
    CO_adsorption = pz.ElementaryReaction(site_types=["1"],
                                    initial=[s0,CO_gas],
                                    final=[CO_ads],
                                    reversible=False,
                                    pre_expon=10.0,
                                    label="CO_adsorption")

    # O2_adsorption:
    O2_adsorption = pz.ElementaryReaction(site_types=["1", "1"],
                                        initial=[s0,s0,O2_gas],
                                        final=[O_ads,O_ads],
                                        neighboring=[(1, 2)],
                                        reversible=False,
                                        pre_expon=2.5,
                                        label="O2_adsorption")

    # CO_oxidation:
    CO_oxidation = pz.ElementaryReaction(site_types=["1", "1"],
                                    initial=[CO_ads, O_ads],
                                    final=[s0, s0, CO2_gas],
                                    neighboring=[(1, 2)],
                                    reversible=False,
                                    pre_expon=1.0e+20,
                                    label="CO_oxidation")

    # Settings:
    sett = pz.Settings()
    sett.molar_fraction.CO = 0.45
    sett.molar_fraction.O2 = 0.55
    sett.random_seed = 953129
    sett.temperature = 500.0
    sett.pressure = 1.0
    sett.snapshots = ('time', 0.1)
    sett.process_statistics = ('time', 0.1)
    sett.species_numbers = ('time', 0.1)
    sett.event_report = 'off'
    sett.max_steps = 'infinity'
    sett.max_time = 1.0
    sett.wall_time = 3600

    job = pz.ZacrosJob( settings=sett,
                        lattice=myLattice,
                        mechanism=[CO_adsorption, O2_adsorption, CO_oxidation],
                        cluster_expansion=[CO_point, O_point] )

    #-----------------------
    # Running the job
    #-----------------------
    results = job.run()

    if( not job.ok() ):
        print( "Warning: The calculation FAILED likely because Zacros executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        job = scm.plams.load( RUNDIR+"/tests/test_ZacrosResults.data/plamsjob.dill" )
        results = job.results

    #-----------------------
    # Analyzing the results
    #-----------------------
    reactions = results.get_reaction_network()

    assert( list(reactions.keys()) == ['CO_adsorption', 'O2_adsorption', 'CO_oxidation'] )

    assert( list(reactions.values()) == \
            ['CO + *(StTp1) -> CO*(StTp1)',
             'O2 + *(StTp1) + *(StTp1) -> O*(StTp1) + O*(StTp1)',
             'CO*(StTp1) + O*(StTp1) -> CO2 + *(StTp1) + *(StTp1)'] )

    provided_quantities = results.provided_quantities()

    assert( list(provided_quantities.keys()) == \
            ['Entry', 'Nevents', 'Time', 'Temperature', 'Energy', 'CO*', 'O*', 'CO', 'O2', 'CO2'] )

    assert( provided_quantities["Time"][0:5] == [0.0, 0.1, 0.2, 0.30000000000000004, 0.4] )

    assert( provided_quantities["Energy"][0:5] == \
            [0.0, -362.40000000000106, -435.4000000000014, -481.8000000000016, -531.5000000000013] )

    assert( provided_quantities["CO*"][0:5] == [0, 24, 20, 15, 9] )

    assert( provided_quantities["CO2"][0:5] == [0, 100, 202, 309, 398] )

    assert( results.gas_species_names() == [ "CO", "O2", "CO2" ] )

    assert( results.surface_species_names() == [ "CO*", "O*" ] )

    assert( results.site_type_names() == [ "StTp1" ] )

    lattice_states = results.lattice_states()
    lattice_states[3].plot( pause=2, close=True )

    results.plot_lattice_states( pause=2, close=True )

    results.plot_molecule_numbers( results.gas_species_names(), pause=2, close=True )

    process_statistics = results.get_process_statistics()

    assert( process_statistics[1]["time"] == 0.1 )
    assert( process_statistics[10]["occurence_frequency"] ==
           {'CO_adsorption': 837.0000000000001, 'O2_adsorption': 550.0000000000001, 'CO_oxidation': 835.0000000000001} )
    assert( process_statistics[10]["number_of_events"] ==
           {'CO_adsorption': 837, 'O2_adsorption': 550, 'CO_oxidation': 835} )

    results.plot_process_statistics( process_statistics[10], key="occurence_frequency", log_scale=True, pause=2, close=True )
    results.plot_process_statistics( process_statistics[10], key="number_of_events", pause=2, close=True )

    scm.plams.finish()
