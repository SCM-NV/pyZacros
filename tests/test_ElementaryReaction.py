#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

from pyzacros.classes.Species import Species
from pyzacros.classes.SpeciesList import SpeciesList
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.ElementaryReaction import ElementaryReaction


def test_ElementaryReaction():
    """Test of the ElementaryReaction class."""
    print( "---------------------------------------------------" )
    print( ">>> Testing ElementaryReaction class" )
    print( "---------------------------------------------------" )

    s0 = Species( "*", 1 )      # Empty adsorption site
    s1 = Species( "H*", 1 )  # H adsorbed with dentation 1
    s2 = Species( "H2*", 1 ) # H2 adsorbed with dentation 1

    myCluster1 = Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=SpeciesList( [s1, s1] ),
                            multiplicity=2,
                            cluster_energy=0.1 )

    myCluster2 = Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=SpeciesList( [s2, s0] ),
                            multiplicity=2,
                            cluster_energy=0.1 )

    myReaction1 = ElementaryReaction( site_types=( "f", "f" ),
                                        neighboring=[ (1,2) ],
                                        initial=myCluster1,
                                        final=myCluster2,
                                        reversible=True,
                                        pre_expon=1e+13,
                                        pe_ratio=0.676,
                                        activation_energy=0.2 )

    print( myReaction1 )

    output = str(myReaction1)
    expectedOutput = """\
reversible_step H2*-f,*-f:(1,2)<-->H*-f,H*-f:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 H* 1
    2 H* 1
  final
    1 H2* 1
    2 * 1
  site_types f f
  pre_expon 1.00000e+13
  pe_ratio 0.67600
  activ_eng 0.20000
end_step\
"""
    assert( output == expectedOutput )

    s3 = Species( "H2", gas_energy=0.0 ) # H2(gas)

    myCluster3 = Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=SpeciesList( [ s0, s0 ] ),
                            gas_species=SpeciesList( [ s3 ] ),
                            multiplicity=2,
                            cluster_energy=0.1 )

    myReaction2 = ElementaryReaction( site_types=( "f", "f" ),
                                        neighboring=[ (1,2) ],
                                        initial=myCluster1,
                                        final=myCluster3,
                                        reversible=False,
                                        pre_expon=1e+13,
                                        pe_ratio=0.676,
                                        activation_energy=0.2 )

    print( myReaction2 )

    output = str(myReaction2)
    expectedOutput = """\
step H*-f,H*-f:(1,2)-->*-f,*-f:H2:(1,2)
  gas_reacs_prods H2 1
  sites 2
  neighboring 1-2
  initial
    1 H* 1
    2 H* 1
  final
    1 * 1
    2 * 1
  site_types f f
  pre_expon 1.00000e+13
  pe_ratio 0.67600
  activ_eng 0.20000
end_step\
"""
    assert( output == expectedOutput )
