#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import random

from pyzacros.classes.Species import Species
from pyzacros.classes.SpeciesList import SpeciesList
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.Mechanism import Mechanism
from pyzacros.classes.Lattice import Lattice
from pyzacros.classes.InitialState import InitialState


def test_Lattice():
    """Test of the Lattice class."""
    print("---------------------------------------------------")
    print(">>> Testing InitialState class")
    print("---------------------------------------------------")

    s0 = Species( "*", 1 )   # Empty adsorption site
    s1 = Species( "H*", 1 )  # H adsorbed with dentation 1
    s2 = Species( "H2*", 1 ) # H2 adsorbed with dentation 1

    myCluster1 = Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=SpeciesList( [ s1, s1 ] ),
                            multiplicity=2,
                            cluster_energy=0.1 )

    myCluster2 = Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=SpeciesList( [ s2, s0 ] ),
                            multiplicity=2,
                            cluster_energy=0.1 )

    myReaction = ElementaryReaction( site_types=( "f", "f" ),
                                        neighboring=[ (1,2) ],
                                        initial=myCluster1,
                                        final=myCluster2,
                                        reversible=True,
                                        pre_expon=1e+13,
                                        pe_ratio=0.676,
                                        activation_energy = 0.2 )

    myMechanism = Mechanism()
    myMechanism.append( myReaction )

    myLattice = Lattice(lattice_type="periodic_cell",
                        cell_vectors=[[2.814, 0.000],[1.407, 2.437]],
                        repeat_cell=[3, 3],
                        n_cell_sites=2,
                        n_site_types=2,
                        site_type_names=["fcc", "hcp"],
                        site_types=["fcc", "hcp"],
                        site_coordinates=[[0.33333,0.33333],[0.66667,0.66667]],
                        neighboring_structure=[["1-1", "north"],
                                               ["1-1", "east"],
                                               ["1-1", "southeast"],
                                               ["2-1", "self"],
                                               ["2-1", "east"],
                                               ["2-1", "north"],
                                               ["2-2", "north"],
                                               ["2-2", "east"],
                                               ["2-2", "southeast"]])

    myInitialState = InitialState( myLattice, myMechanism )

    random.seed(10)
    myInitialState.fillSites( site_name="fcc", species="H*", coverage=0.5 )
    myInitialState.fillSites( site_name="fcc", species=s2, coverage=0.5 )
    myInitialState.fillSites( site_name="hcp", species="H*", coverage=1.0 )

    print( myInitialState )

    output = str(myInitialState)

    expectedOutput = """\
initial_state
  seed_on_sites H* 2
  seed_on_sites H* 3
  seed_on_sites H* 4
  seed_on_sites H* 5
  seed_on_sites H* 6
  seed_on_sites H* 8
  seed_on_sites H* 10
  seed_on_sites H* 11
  seed_on_sites H* 12
  seed_on_sites H* 14
  seed_on_sites H* 15
  seed_on_sites H* 16
  seed_on_sites H* 18
  seed_on_sites H2* 1
  seed_on_sites H2* 7
  seed_on_sites H2* 13
  seed_on_sites H2* 17
end_initial_state\
"""
    assert(output == expectedOutput)
