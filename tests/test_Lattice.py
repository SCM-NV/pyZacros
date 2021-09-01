#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import pyzacros as pz
from pyzacros.utils.compareReports import compare


def test_Lattice():
    """Test of the Lattice class."""
    print("---------------------------------------------------")
    print(">>> Testing Lattice class")
    print("---------------------------------------------------")

    myLattice = pz.Lattice( cell_vectors=[[2.77185866, 0.00000000],[1.38592933, 2.40050002]],
                            repeat_cell=[4, 4],
                            site_types=["b", "h", "b", "b", "f", "t"],
                            site_coordinates=[[0.00001, 0.49999],
                                              [0.33333, 0.33333],
                                              [0.49999, 0.00001],
                                              [0.49999, 0.49999],
                                              [0.66667, 0.66667],
                                              [0.99999, 0.00001]],
                            neighboring_structure=[ [(0,1), pz.Lattice.SELF],
                                                    [(1,2), pz.Lattice.SELF],
                                                    [(1,3), pz.Lattice.SELF],
                                                    [(3,4), pz.Lattice.SELF],
                                                    [(4,2), pz.Lattice.NORTH],
                                                    [(4,0), pz.Lattice.EAST],
                                                    [(5,5), pz.Lattice.NORTH],
                                                    [(5,5), pz.Lattice.EAST],
                                                    [(5,4), pz.Lattice.SELF],
                                                    [(5,1), pz.Lattice.SELF],
                                                    [(5,1), pz.Lattice.EAST],
                                                    [(5,4), pz.Lattice.SOUTHEAST],
                                                    [(5,1), pz.Lattice.SOUTHEAST],
                                                    [(4,5), pz.Lattice.NORTH],
                                                    [(5,5), pz.Lattice.SOUTHEAST] ] )

    print(myLattice)
    myLattice.plot( pause=2 )

    output = str(myLattice)
    expectedOutput = """\
lattice periodic_cell
cell_vectors
  2.77185866  0.00000000
  1.38592933  2.40050002
repeat_cell 4 4
n_site_types 4
site_type_names b f h t
n_cell_sites 6
site_types b h b b f t
site_coordinates
  0.00001000  0.49999000
  0.33333000  0.33333000
  0.49999000  0.00001000
  0.49999000  0.49999000
  0.66667000  0.66667000
  0.99999000  0.00001000
neighboring_structure
  1-2  self
  2-3  self
  2-4  self
  4-5  self
  5-3  north
  5-1  east
  6-6  north
  6-6  east
  6-5  self
  6-2  self
  6-2  east
  6-5  southeast
  6-2  southeast
  5-6  north
  6-6  southeast
end_neighboring_structure
end_lattice\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )

    ## reading from yaml
    #myLattice = pz.Lattice(path_to_slab_yaml="./pyzacros/slabs/pd111.yaml")
    #output2 = str(myLattice)
    #assert( compare( output2, expectedOutput, 1e-3 ) )

test_Lattice()
