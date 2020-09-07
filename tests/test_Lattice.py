#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

from pyzacros.classes.Lattice import Lattice


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
lattice\tperiodic_cell
cell_vectors
\t2.814284989122459\t0.0
\t1.407142494561229\t2.437242294069262
repeat_cell\t23 24
n_cell_sites\t2
n_site_types\t2
site_type_names\tfcc hcp
site_types\t1 2
site_coordinates
\t0.333333333333333\t0.333333333333333
\t0.666666666666666\t0.666666666666666
neighboring_structure
\t1-1 north
\t1-1 east
\t1-1 southeast
\t2-1 self
\t2-1 east
\t2-1 north
\t2-2 north
\t2-2 east
\t2-2 southeast
end_neighboring_structure
end_lattice\
"""
    assert(output == expectedOutput)

    # reading from yaml
    myLattice = Lattice(path_to_slab_yaml="./pyzacros/slabs/pd111.yaml")
    output2 = str(myLattice)
    assert(output2 == expectedOutput)
