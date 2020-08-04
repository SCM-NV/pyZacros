#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.Species import Species


def test_Cluster():
    """Test of the Cluster class."""
    print("---------------------------------------------------")
    print(">>> Testing Cluster class")
    print("---------------------------------------------------")
    myCluster1 = Cluster(site_types=("f", "f"),
                         neighboring=[(1, 2)],
                         species=(Species("H*", 1), Species("H*", 1)),
                         multiplicity=2,
                         cluster_energy=0.1)

    print(myCluster1)

    output = str(myCluster1)
    expectedOutput = """\
cluster H*-f,H*-f:(1,2)
  sites 2
  neighboring 1-2
  lattice_state
    1 H* 1
    2 H* 1
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1
end_cluster\
"""
    assert(output == expectedOutput)

    myCluster2 = Cluster(site_types=("f", "f"),
                         neighboring=[(1, 2)],
                         species=[Species("H*", 1), Species("H*", 1)],
                         gas_species=[Species("H2", gas_energy=0.0)],
                         multiplicity=2,
                         cluster_energy=0.1)

    print(myCluster2)

    output = str(myCluster2)
    expectedOutput = """\
cluster H*-f,H*-f:H2:(1,2)
  # gas_species H2
  sites 2
  neighboring 1-2
  lattice_state
    1 H* 1
    2 H* 1
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1
end_cluster\
"""
    assert(output == expectedOutput)