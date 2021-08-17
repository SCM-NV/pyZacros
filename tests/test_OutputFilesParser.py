#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import os
import sys
import shutil

import pyzacros as pz
from pyzacros.utils.compareReports import compare


RUNDIR=None

def test_OutputFilesParser():
    global RUNDIR
    RUNDIR = os.getcwd()

    print( "---------------------------------------------------" )
    print( ">>> Testing OutputFilesParser class" )
    print( "---------------------------------------------------" )

    parser = pz.OutputFilesParser( RUNDIR+"/tests/test_OutputFilesParser.data" )

    output  = str( parser )

    print(output)

    expectedOutput = """\
random_seed = 123278
gas_specs_names = ['CO', 'H2', 'H2O', 'CO2']
gas_energies = [0.0, 0.0, 0.0, -0.615]
gas_molec_weights = [27.9949, 2.0156, 18.0105, 43.9898]
gas_molar_fracs = [1e-05, 0.0, 0.95, 0.0]
surf_specs_names = ['CO*', 'H*', 'H2O*', 'OH*', 'O*', 'COOH*']
surf_specs_dent = [1, 1, 1, 1, 1, 1]
max_steps = inf
max_time = 250.0
wall_time = 30\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )

test_OutputFilesParser()
