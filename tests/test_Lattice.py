#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import scm.pyzacros as pz
from scm.pyzacros.utils.compareReports import compare


def test_Lattice():
    """Test of the Lattice class."""
    print("---------------------------------------------------")
    print(">>> Testing Lattice class")
    print("---------------------------------------------------")

    print("")
    print("From default lattices")
    print("---------------------")
    myLattice = pz.Lattice( lattice_type=pz.Lattice.HEXAGONAL, lattice_constant=1.0, repeat_cell=[8,10] )

    print(myLattice)
    myLattice.plot( pause=2, close=True )

    output = str(myLattice)
    expectedOutput = """\
lattice default_choice
  hexagonal_periodic 1.0 8 10
end_lattice\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )

    print("")
    print("From unit-cell")
    print("--------------")
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
    myLattice.plot( pause=2, close=True )

    output = str(myLattice)
    expectedOutput = """\
lattice periodic_cell
  cell_vectors
    2.77185866    0.00000000
    1.38592933    2.40050002
  repeat_cell 4 4
  n_site_types 4
  site_type_names b f h t
  n_cell_sites 6
  site_types b h b b f t
  site_coordinates
    0.00001000    0.49999000
    0.33333000    0.33333000
    0.49999000    0.00001000
    0.49999000    0.49999000
    0.66667000    0.66667000
    0.99999000    0.00001000
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

    print("")
    print("From explicitly defined lattices")
    print("--------------------------------")

    myLattice = pz.Lattice( site_types=["cn2", "br42", "cn4", "br42", "cn2", "br42", "br44", "br44",
                                       "br42", "cn4", "br44", "cn4", "br42", "br42", "cn2"],
                            site_coordinates=[[0.0000e+0, 0.0000e+0],
                                              [1.4425e+0, 0.0000e+0],
                                              [2.8850e+0, 0.0000e+0],
                                              [4.3275e+0, 0.0000e+0],
                                              [5.7700e+0, 0.0000e+0],
                                              [7.2125e-1, 1.2492e+0],
                                              [2.1637e+0, 1.2492e+0],
                                              [3.6062e+0, 1.2492e+0],
                                              [5.0487e+0, 1.2492e+0],
                                              [1.4425e+0, 2.4985e+0],
                                              [2.8850e+0, 2.4985e+0],
                                              [4.3275e+0, 2.4985e+0],
                                              [2.1637e+0, 3.7477e+0],
                                              [3.6062e+0, 3.7477e+0],
                                              [2.8850e+0, 4.9970e+0]],
                            nearest_neighbors=[[ 1,  5],
                                               [ 0,  2],
                                               [ 1,  3,  6, 7],
                                               [ 2,  4],
                                               [ 3,  8],
                                               [ 0,  9],
                                               [ 2,  9],
                                               [ 2, 11],
                                               [ 4, 11],
                                               [ 5,  6, 10, 12],
                                               [ 9, 11],
                                               [ 7,  8, 10, 13],
                                               [ 9, 14],
                                               [11, 14],
                                               [12, 13]] )

    print(myLattice)
    myLattice.plot( pause=2, close=True )

    output = str(myLattice)
    expectedOutput = """\
lattice explicit
  n_sites 15
  max_coord 4
  n_site_types 4
  site_type_names br42 br44 cn2 cn4
  lattice_structure
       1  0.00000000  0.00000000         cn2     2     2     6
       2  1.44250000  0.00000000        br42     2     1     3
       3  2.88500000  0.00000000         cn4     4     2     4     7     8
       4  4.32750000  0.00000000        br42     2     3     5
       5  5.77000000  0.00000000         cn2     2     4     9
       6  0.72125000  1.24920000        br42     2     1    10
       7  2.16370000  1.24920000        br44     2     3    10
       8  3.60620000  1.24920000        br44     2     3    12
       9  5.04870000  1.24920000        br42     2     5    12
      10  1.44250000  2.49850000         cn4     4     6     7    11    13
      11  2.88500000  2.49850000        br44     2    10    12
      12  4.32750000  2.49850000         cn4     4     8     9    11    14
      13  2.16370000  3.74770000        br42     2    10    15
      14  3.60620000  3.74770000        br42     2    12    15
      15  2.88500000  4.99700000         cn2     2    13    14
  end_lattice_structure
end_lattice\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )

    ## reading from yaml
    #myLattice = pz.Lattice(path_to_slab_yaml="./pyzacros/slabs/pd111.yaml")
    #output2 = str(myLattice)
    #assert( compare( output2, expectedOutput, 1e-3 ) )
