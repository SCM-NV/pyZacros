#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import scm.plams

import pyzacros as pz
from pyzacros.utils.compareReports import compare

def test_KMCJob2_run():
    """Test of the KMCJob2.run method."""
    print( "---------------------------------------------------" )
    print( ">>> Testing KMCJob2.run method" )
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
    myLattice = pz.Lattice(lattice_type="default_choice",
                        default_lattice=["rectangular_periodic", 1.0, 50, 50])

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
                                    pre_expon=10.0)

    # O2_adsorption:
    O2_adsorption = pz.ElementaryReaction(site_types=["1", "1"],
                                        initial=[s0,s0,O2_gas],
                                        final=[O_ads,O_ads],
                                        neighboring=[(1, 2)],
                                        reversible=False,
                                        pre_expon=2.5)

    # CO_oxidation:
    CO_oxidation = pz.ElementaryReaction(site_types=["1", "1"],
                                    initial=[CO_ads, O_ads],
                                    final=[s0, s0, CO2_gas],
                                    neighboring=[(1, 2)],
                                    reversible=False,
                                    pre_expon=1.0e+20)

    # Settings:
    sett = pz.Settings()
    sett.molar_fraction.CO = 0.45
    sett.molar_fraction.O2 = 0.55
    sett.random_seed = 953129
    sett.temperature = 500.0
    sett.pressure = 1.0
    sett.snapshots = ('time', 5.e-1)
    sett.process_statistics = ('time', 1.e-2)
    sett.species_numbers = ('time', 1.e-2)
    sett.event_report = 'off'
    sett.max_steps = 'infinity'
    sett.max_time = 25.0
    sett.wall_time = 3600

    job = pz.KMCJob2( settings=sett,
                      lattice=myLattice,
                      mechanism=[CO_adsorption, O2_adsorption, CO_oxidation],
                      cluster_expansion=[CO_point, O_point] )

    print(job)
    results = job.run()

    #if( not job.ok() ): raise Exception( "Zacros calculation FAILED!" )

    #print( results.reactions )
    ## [ "*-1:CO-->CO*-1", "*-1,*-1:O2-->O*-1,O*-1;(1,2)", "CO*-1,O*-1-->*-1,*-1:CO2;(1,2)" ]
    #results.provided_quantities
    ## [ "Entry", "Nevents", "Time", "Temperature", "Energy", "CO*", "O*", "CO", "O2", "CO2" ]

    #results.gas_species_names # [ "CO", "O2", "CO2" ]
    #results.surface_species_names # [ "CO*", "O*" ]
    #results.site_types # [ "StTp1" ]
    #results.energetic_interaction_clusters # 2
    #results.elementary_events # 3
    ##results.lattice #
    #results.time # [ 0.0, 0.5, 1.0, ... ]
    #results.addlayer_configuration # [ latticeState0, latticeState1, ... ]
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

test_KMCJob2_run()
