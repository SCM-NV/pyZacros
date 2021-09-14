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
    expectedOutput = """\
---------------------------------------------------------------------
simulation_input.dat
---------------------------------------------------------------------
random_seed             10
temperature          380.0
pressure               2.0

n_gas_species   1
gas_specs_names           H2
gas_energies             0.0
gas_molec_weights     2.0156
gas_molar_fracs          0.0

n_surf_species    2
surf_specs_names          H*       H2*
surf_specs_dent            1         1

snapshots                 on time       1e-05
process_statistics        on time       1e-05
species_numbers           on time       1e-05
event_report      off
max_steps         infinity
max_time          100.0
wall_time         5000

finish
---------------------------------------------------------------------
lattice_input.dat
---------------------------------------------------------------------
lattice default_choice
hexagonal_periodic 1.0 8 10
end_lattice
---------------------------------------------------------------------
energetics_input.dat
---------------------------------------------------------------------
energetics

cluster H*_0-f,H*_1-f:(1,2)
  sites 2
  neighboring 1-2
  lattice_state
    1 H* 1
    2 H* 1
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1000
end_cluster

cluster H2*_0-f,*_1-f:(1,2)
  sites 2
  neighboring 1-2
  lattice_state
    1 H2* 1
    2 * 1
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1000
end_cluster

cluster *_0-f,*_1-f:(1,2)
  sites 2
  neighboring 1-2
  lattice_state
    1 * 1
    2 * 1
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1000
end_cluster

end_energetics
---------------------------------------------------------------------
mechanism_input.dat
---------------------------------------------------------------------
mechanism

reversible_step H2*-f,*-f<-->H*-f,H*-f;(1,2)
  sites 2
  neighboring 1-2
  initial
    1 H* 1
    2 H* 1
  final
    1 H2* 1
    2 * 1
  site_types f f
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.2
end_reversible_step

step H2*-f,*-f-->*-f,*-f:H2;(1,2)
  gas_reacs_prods H2 1
  sites 2
  neighboring 1-2
  initial
    1 H2* 1
    2 * 1
  final
    1 * 1
    2 * 1
  site_types f f
  pre_expon 1.000000e+13
  activ_eng 0.2
end_step

end_mechanism\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )

    #myJob = pz.ZacrosJob.load_external( path='test_ZacrosJob.data/default' )
    #print(myJob)
    #myJob = pz.ZacrosJob.load_external( path='test_ZacrosJob.data/periodic_cell' )
    #print(myJob)
    #myJob = pz.ZacrosJob.load_external( path='test_ZacrosJob.data/explicit' )
    #print(myJob)

test_ZacrosJob()
