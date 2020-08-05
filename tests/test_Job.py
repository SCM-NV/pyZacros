#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

from pyzacros.classes.Species import Species
from pyzacros.classes.SpeciesList import SpeciesList
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.Mechanism import Mechanism
from pyzacros.classes.Job import Job


def test_Job():
    """Test of the Mechanism class."""
    print( "---------------------------------------------------" )
    print( ">>> Testing Job class" )
    print( "---------------------------------------------------" )

    s0 = Species( "*" )      # Empty adsorption site
    s1 = Species( "H*", 1 )  # H adsorbed with dentation 1
    s2 = Species( "H2*", 1 ) # H2 adsorbed with dentation 1
    s3 = Species( "H2", gas_energy=0.0 ) # H2(gas)

    myCluster1 = Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=SpeciesList( [ s1, s1 ] ),
                            multiplicity=2,
                            cluster_energy=0.1 )

    myCluster2 = Cluster( site_types=( "f", "f" ),
                            neighboring=SpeciesList( [ (1,2) ] ),
                            species=[ s2, s0 ],
                            multiplicity=2,
                            cluster_energy=0.1 )

    myCluster3 = Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=SpeciesList( [ s0, s0 ] ),
                            gas_species=[ s3 ],
                            multiplicity=2,
                            cluster_energy=0.1 )

    myReaction1 = ElementaryReaction( site_types=( "f", "f" ),
                                        neighboring=[ (1,2) ],
                                        initial=myCluster1,
                                        final=myCluster2,
                                        reversible=True,
                                        pre_expon=1e+13,
                                        pe_ratio=0.676,
                                        activation_energy = 0.2 )

    myReaction2 = ElementaryReaction( site_types=( "f", "f" ),
                                        neighboring=[ (1,2) ],
                                        initial=myCluster2,
                                        final=myCluster3,
                                        reversible=False,
                                        pre_expon=1e+13,
                                        pe_ratio=0.676,
                                        activation_energy = 0.2 )

    myMechanism = Mechanism()
    myMechanism.append( myReaction1 )
    myMechanism.append( myReaction2 )

    myJob = Job( myMechanism )
    print(myJob)

    myJob.writeInputFiles()

    output = str(myJob)
    expectedOutput = """\
---------------------------
simulation_input.dat
---------------------------
random_seed 10
temperature 380.0
pressure 2.00

n_gas_species 1
gas_specs_names           H2
gas_energies             0.0
gas_molec_weights        XXX

n_surf_species 2
surf_specs_names          H*       H2*
surf_specs_dent            1         1

snapshots on time 1e-5
process_statistics on time 1e-5
species_numbers on time 1e-5
event_report off
max_steps infinity
max_time 1.0e+2
wall_time 5000

finish
---------------------------
lattice_input.dat
---------------------------

---------------------------
energetics_input.dat
---------------------------
energetics
cluster H*-f,H*-f:(1,2)
  sites 2
  neighboring 1-2
  lattice_state
    1 H* 1
    2 H* 1
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1
end_cluster
cluster H2*-f,*-f:(1,2)
  sites 2
  neighboring 1-2
  lattice_state
    1 H2* 1
    2 * 0
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1
end_cluster
cluster *-f,*-f:H2:(1,2)
  # gas_species H2
  sites 2
  neighboring 1-2
  lattice_state
    1 * 0
    2 * 0
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1
end_cluster
end energetics
---------------------------
mechanism_input.dat
---------------------------
mechanism
reversible_step H*-f,H*-f:(1,2)<-->H2*-f,*-f:(1,2)
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
end_step
step H2*-f,*-f:(1,2)-->*-f,*-f:H2:(1,2)
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
  pe_ratio 0.676
  activ_eng 0.2
end_step
end_mechanism\
"""
    assert( output == expectedOutput )
