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
    # Plotting the lattice
    #-----------------------
    job.lattice.plot( pause=2, close=True)

    results = job.run()

    if( not job.ok() ):
        print( "Warning: The calculation FAILED likely because Zacros executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        job = scm.plams.load( RUNDIR+"/tests/test_ZacrosResults.data/plamsjob.dill" )
        results = job.results

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

    try:
        import matplotlib.pyplot as plt

        #-----------------------------------------------
        # Plotting the lattice states as an animation
        #-----------------------------------------------
        plt.rcParams["figure.autolayout"] = True
        fig, ax = plt.subplots()
        for i,ls in enumerate(results.lattice_states()):
            ax.cla()
            ls.plot( show=True, pause=0.5, ax=ax )
        plt.pause(2)
        plt.close("all")

        #------------------------------------------------------
        # Plotting the Molecule Numbers as a function of time
        #------------------------------------------------------
        x_len = abs(max(provided_quantities["Time"])-min(provided_quantities["Time"]))
        y_len = abs(max(provided_quantities["CO*"])-min(provided_quantities["CO*"]))

        fig,ax = plt.subplots()
        ax.set_xlabel('t (s)')
        ax.set_ylabel('Molecule Numbers')
        ax.step(provided_quantities["Time"], provided_quantities["CO*"], color='r', label="CO*")
        ax.step(provided_quantities["Time"],  provided_quantities["O*"], color='b', label="O*")
        ax.legend(loc='best')
        plt.pause(2)
        plt.close("all")

    except ImportError as e:
        pass

    #results.forward_rates
    #results.reverse_rates
    #results.net_forward_rates
    #results.net_reverse_rates
    #results.single_occurence_threshold
    #results.nevents
    #Results.normalize(results.nevents, norm_factor=2500)
    #Results.normalize(results.nevents, norm_factor_by_site_type="StTp1")
    #results.temperature
    #results.energy
    #Results.normalize(results.energy,norm_factor=2500)
    #Results.normalize(results.energy, norm_factor_by_site_type="StTp1")
    #results.surface_species  # Dict {"O*":[10,35,...],"CO*":[1,4,...]}
    #results.gas_species # Dict
    #results.

    #results.configuration["time"] # [0.0, 0.5, 1.0, ...]
    #results.configuration["lattice_state"] # [ latticeState0, latticeState1, ... ]

    ##output = str(myJob)
    ##expectedOutput = """\
##\
##"""
    ##assert( compare( output, expectedOutput, 1e-3 ) )

    scm.plams.finish()

test_ZacrosJob_run()
