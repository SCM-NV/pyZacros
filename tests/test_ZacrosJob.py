#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import pyzacros as pz
from pyzacros.utils.compareReports import compare


def test_ZacrosJob():
    """Test of the Mechanism class."""
    print( "---------------------------------------------------" )
    print( ">>> Testing ZacrosJob class" )
    print( "---------------------------------------------------" )

    s0 = pz.Species( "*", 1 )   # Empty adsorption site
    s1 = pz.Species( "H*", 1 )  # H adsorbed with dentation 1
    s2 = pz.Species( "H2*", 1 ) # H2 adsorbed with dentation 1
    s3 = pz.Species( "H2", gas_energy=0.0 ) # H2(gas)

    myLattice = pz.Lattice(lattice_type=pz.Lattice.HEXAGONAL, lattice_constant=1.0, repeat_cell=[8,10])

    myCluster1 = pz.Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=[ s1, s1 ],
                            multiplicity=2,
                            cluster_energy=0.1 )

    myCluster2 = pz.Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=[ s2, s0 ],
                            multiplicity=2,
                            cluster_energy=0.1 )

    myCluster3 = pz.Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=[ s0, s0 ],
                            multiplicity=2,
                            cluster_energy=0.1 )

    myClusterExpansion = pz.ClusterExpansion( [myCluster1, myCluster2, myCluster3] )

    myReaction1 = pz.ElementaryReaction( site_types=( "f", "f" ),
                                        neighboring=[ (1,2) ],
                                        initial=[ s1, s1 ],
                                        final=[ s2, s0 ],
                                        reversible=True,
                                        pre_expon=1e+13,
                                        pe_ratio=0.676,
                                        activation_energy = 0.2 )

    myReaction2 = pz.ElementaryReaction( site_types=( "f", "f" ),
                                        neighboring=[ (1,2) ],
                                        initial=[ s2, s0 ],
                                        final=[ s0, s0, s3 ],
                                        reversible=False,
                                        pre_expon=1e+13,
                                        pe_ratio=0.676,
                                        activation_energy = 0.2 )

    myMechanism = pz.Mechanism()
    myMechanism.append( myReaction1 )
    myMechanism.append( myReaction2 )

    sett = pz.Settings()
    sett.random_seed = 10
    sett.temperature = 380.0
    sett.pressure = 2.00
    sett.snapshots = ('time', 1.e-5)
    sett.process_statistics = ('time', 1.e-5)
    sett.species_numbers = ('time', 1.e-5)
    sett.event_report = 'off'
    sett.max_steps = 'infinity'
    sett.max_time = 100.0
    sett.wall_time = 5000

    myJob = pz.ZacrosJob( myLattice, myMechanism, myClusterExpansion, settings=sett )
    print(myJob)

    output = str(myJob)
    with open( "tests/test_ZacrosJob_expected_output.txt", "r" ) as inp:
        expectedOutput = inp.read()
    assert( compare( output, expectedOutput, 1e-3 ) )

    myJob = pz.ZacrosJob.load_external( path='tests/test_ZacrosJob.data/default' )
    print(myJob)

    output = str(myJob)
    with open( "tests/test_ZacrosJob_expected_output_default.txt", "r" ) as inp:
        expectedOutput = inp.read()
    assert( compare( output, expectedOutput, 1e-3 ) )

    #myJob = pz.ZacrosJob.load_external( path='tests/test_ZacrosJob.data/periodic_cell' )
    #print(myJob)
    #myJob = pz.ZacrosJob.load_external( path='tests/test_ZacrosJob.data/explicit' )
    #print(myJob)

test_ZacrosJob()
