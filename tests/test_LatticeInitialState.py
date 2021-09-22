#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import random

import pyzacros as pz
from pyzacros.utils.compareReports import compare


def test_InitialState():
    """Test of the Lattice class."""
    print("---------------------------------------------------")
    print(">>> Testing InitialState class")
    print("---------------------------------------------------")

    s0 = pz.Species( "*", 1 )   # Empty adsorption site
    s1 = pz.Species( "H*", 1 )  # H adsorbed with dentation 1
    s2 = pz.Species( "H2**", 2 ) # H2 adsorbed with dentation 1

    lattice = pz.Lattice(cell_vectors=[[2.814, 0.000],[1.407, 2.437]],
                           repeat_cell=[3, 3],
                           site_types=["fcc", "hcp"],
                           site_coordinates=[[0.33333,0.33333],[0.66667,0.66667]],
                           neighboring_structure=[[(0,0), pz.Lattice.NORTH],
                                                  [(0,0), pz.Lattice.EAST],
                                                  [(0,0), pz.Lattice.SOUTHEAST],
                                                  [(1,0), pz.Lattice.SELF],
                                                  [(1,0), pz.Lattice.EAST],
                                                  [(1,0), pz.Lattice.NORTH],
                                                  [(1,1), pz.Lattice.NORTH],
                                                  [(1,1), pz.Lattice.EAST],
                                                  [(1,1), pz.Lattice.SOUTHEAST]])

    lattice.plot( show_sites_ids=True, pause=2, close=True )
    initialState = pz.LatticeState( lattice, [s0,s1,s2] )

    random.seed(10)
    initialState.fill_sites_random( site_name="fcc", species="H*", coverage=0.5 )
    initialState.fill_sites_random( site_name=("fcc","hcp"), species=s2, coverage=0.5 )
    initialState.fill_site( (0,1), s2 )
    initialState.fill_sites_random( site_name="hcp", species="H*", coverage=1.0 )
    initialState.plot( pause=2, show_sites_ids=True, close=True )

    print( initialState )

    output = str(initialState)

    expectedOutput = """\
initial_state
  # species * H* H2**
  # species_numbers
  #   - H2**  8
  #   - H*  8
  seed_on_sites H2** 1 2
  seed_on_sites H* 3
  seed_on_sites H* 4
  seed_on_sites H* 5
  seed_on_sites H* 6
  seed_on_sites H2** 8 14
  seed_on_sites H2** 9 13
  seed_on_sites H* 10
  seed_on_sites H* 11
  seed_on_sites H2** 12 16
  seed_on_sites H* 15
  seed_on_sites H* 18
end_initial_state\
"""
    assert(output == expectedOutput)
