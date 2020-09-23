#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

from pyzacros.classes.Species import Species
from pyzacros.classes.SpeciesList import SpeciesList
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.Mechanism import Mechanism
from pyzacros.utils.compareReports import *


def test_Mechanism():
    """Test of the Mechanism class."""
    print( "---------------------------------------------------" )
    print( ">>> Testing Mechanism class" )
    print( "---------------------------------------------------" )

    s0 = Species( "*", 1 )      # Empty adsorption site
    s1 = Species( "H*", 1 )  # H adsorbed with dentation 1
    s2 = Species( "H2*", 1 ) # H2 adsorbed with dentation 1
    s3 = Species( "H2*", 2 ) # H2 adsorbed with dentation 2

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

    myCluster3 = Cluster( site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=SpeciesList( [ s3 ] ),
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
                                        initial=myCluster3,
                                        final=myCluster2,
                                        reversible=True,
                                        pre_expon=1e+13,
                                        pe_ratio=0.676,
                                        activation_energy = 0.2 )

    myMechanism = Mechanism()
    myMechanism.append( myReaction1 )
    myMechanism.append( myReaction2 )

    print( myMechanism )

    output = str(myMechanism)

    expectedOutput = """\
mechanism
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
  pre_expon 1.000e+13
  pe_ratio 0.676
  activ_eng 0.200
end_step
reversible_step H2*-f-f:(1,2)<-->H2*-f,*-f:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 H2* 1
    1 H2* 2
  final
    1 H2* 1
    2 * 1
  site_types f f
  pre_expon 1.000e+13
  pe_ratio 0.676
  activ_eng 0.200
end_step
end_mechanism\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )
