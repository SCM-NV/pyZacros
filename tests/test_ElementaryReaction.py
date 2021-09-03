#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import pyzacros as pz
from pyzacros.utils.compareReports import compare


def test_ElementaryReaction():
    """Test of the ElementaryReaction class."""
    print( "---------------------------------------------------" )
    print( ">>> Testing ElementaryReaction class" )
    print( "---------------------------------------------------" )

    s0 = pz.Species( "*", 1 )      # Empty adsorption site
    s1 = pz.Species( "H*", 1 )  # H adsorbed with dentation 1
    s2 = pz.Species( "H2*", 1 ) # H2 adsorbed with dentation 1

    myReaction1 = pz.ElementaryReaction( site_types=( "f", "f" ),
                                        neighboring=[ (1,2) ],
                                        initial=[s1, s1],
                                        final=[s2, s0],
                                        reversible=True,
                                        pre_expon=1e+13,
                                        pe_ratio=0.676,
                                        activation_energy=0.2 )

    print( myReaction1 )

    output = str(myReaction1)
    expectedOutput = """\
reversible_step H2*-f,*-f<-->H*-f,H*-f;(1,2)
  sites 2
  neighboring 1-2
  initial
    1 H* 1
    2 H* 1
  final
    1 H2* 1
    2 * 1
  site_types f f
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.2
end_reversible_step\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )

    s3 = pz.Species( "H2", gas_energy=0.0 ) # H2(gas)

    myReaction2 = pz.ElementaryReaction( site_types=( "f", "f" ),
                                        neighboring=[ (1,2) ],
                                        initial=[ s1, s1 ],
                                        final=[ s0, s0, s3 ],
                                        reversible=False,
                                        pre_expon=1e+13,
                                        pe_ratio=0.676,
                                        activation_energy=0.2 )

    print( myReaction2 )

    output = str(myReaction2)
    expectedOutput = """\
step H*-f,H*-f-->*-f,*-f:H2;(1,2)
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
  pre_expon 1.000e+13
  activ_eng 0.200
end_step\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )
