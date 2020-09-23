#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

from pyzacros.classes.Lattice import Lattice
from pyzacros.utils.compareReports import *


def test_Lattice():
    """Test of the Lattice class."""
    print("---------------------------------------------------")
    print(">>> Testing Lattice class")
    print("---------------------------------------------------")

    myLattice = Lattice(lattice_type="periodic_cell",
                        cell_vectors=[[2.814284989122459,  0.000000000000000],
                                      [1.407142494561229, 2.437242294069262]],
                        repeat_cell=[23, 24],
                        n_cell_sites=2,
                        n_site_types=2,
                        site_type_names=["fcc", "hcp"],
                        site_types=[1, 2],
                        site_coordinates=[[0.333333333333333,
                                          0.333333333333333],
                                          [0.666666666666666,
                                           0.666666666666666]],
                        neighboring_structure=[["1-1", "north"],
                                               ["1-1", "east"],
                                               ["1-1", "southeast"],
                                               ["2-1", "self"],
                                               ["2-1", "east"],
                                               ["2-1", "north"],
                                               ["2-2", "north"],
                                               ["2-2", "east"],
                                               ["2-2", "southeast"]])

    print(myLattice)

    output = str(myLattice)
    expectedOutput = """\
lattice periodic_cell
cell_vectors
  2.814  0.000
  1.407  2.437
repeat_cell 23 24
n_cell_sites 2
n_site_types 2
site_type_names fcc hcp
site_types 1 2
site_coordinates
  0.333  0.333
  0.667  0.667
neighboring_structure
  1-1 north
  1-1 east
  1-1 southeast
  2-1 self
  2-1 east
  2-1 north
  2-2 north
  2-2 east
  2-2 southeast
end_neighboring_structure
end_lattice\
"""
    assert(output == expectedOutput)

    # reading from yaml
    myLattice = Lattice(path_to_slab_yaml="./pyzacros/slabs/pd111.yaml")
    output2 = str(myLattice)
    assert( compare( output, expectedOutput, 1e-3 ) )
