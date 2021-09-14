#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import pyzacros as pz
from pyzacros.utils.compareReports import compare


def test_Cluster():
    """Test of the Cluster class."""
    print( "---------------------------------------------------" )
    print( ">>> Testing Cluster class" )
    print( "---------------------------------------------------" )
    cluster = pz.Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=pz.SpeciesList( [ pz.Species("H*",1), pz.Species("H*",1) ] ),
                            multiplicity=2,
                            cluster_energy = 0.1 )

    print( cluster )

    output = str(cluster)
    expectedOutput = """\
cluster H*-f,H*-f:(1,2)
  sites 2
  neighboring 1-2
  lattice_state
    1 H* 1
    2 H* 1
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.100
end_cluster\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )

    cluster = pz.Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=pz.SpeciesList( [ pz.Species("H2*",2) ] ),
                            multiplicity=2,
                            cluster_energy = 0.1 )

    print( cluster )

    output = str(cluster)
    expectedOutput = """\
cluster H2*-f-f:(1,2)
  sites 2
  neighboring 1-2
  lattice_state
    1 H2* 1
    1 H2* 2
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.100
end_cluster\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )

    #cluster = pz.Cluster( site_types=( "f", "f" ),
                            #neighboring=[ (1,2) ],
                            #species=pz.SpeciesList( [ pz.Species("H*",1), pz.Species("H*",1) ] ),
                            #multiplicity=2,
                            #cluster_energy = 0.1 )

    #print( cluster )

    #output = str(cluster)
    #expectedOutput = """\
#cluster CO2**-f-h,H*-i:(1,2),(2,3),(3,4),(1,4),(3,5)
  #sites 5
  #neighboring 1-2 2-3 3-4 4-1 3-5
  #lattice_state
    #1 CO2** 1
    #1 CO2** 2
    #2 H* 1
    #3 *  1
    #4 *  1
  #site_types f g h i j
  #graph_multiplicity 1
  #cluster_eng 0.100
#end_cluster\
#"""
    #assert( compare( output, expectedOutput, 1e-3 ) )

