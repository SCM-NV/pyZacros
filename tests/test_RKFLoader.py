#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import os
import sys
from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.utils.RKFLoader import get_LatticeAndMechanism
from pyzacros.classes.KMCJob import KMCJob


def pyzacros_example():
    """Create pyZacros input files using a default Lattice."""
    # Tries to use PLAMS from AMS
    AMSHOME = os.getenv("AMSHOME")
    if(AMSHOME is not None):
        if(AMSHOME+"/scripting" not in sys.path):
            sys.path.append(AMSHOME+"/scripting")

            # If AMS is available. It runs the calculations to generate
            # both the energy landscape and binding sites. Results are
            # saved in the directory tests/test_RKFLoader.data
            #results = buildEnergyLandscape()
            #results = deriveBindingSites()

        # If AMS is not available, it tries to load the package from PYTHONPATH
    try:
        import scm.plams
    except ImportError:
        raise Exception("Package scm.plams is required!")

    # Results are loaded from tests/test_RKFLoader.data
    scm.plams.init()
    job = scm.plams.AMSJob.load_external(path="tests/test_RKFLoader.data/BindingSites-EON")
    scm.plams.finish()

    (myLattice, myMechanism) = get_LatticeAndMechanism(job.results)
    #
    #    output  = str( myRKFLoader.mechanism )+"\n"
    myLattice.repeat_cell = [2, 2]
    sett = KMCSettings()

    # Settings:
    sett.random_seed = 123278
    sett.temperature = 500.0
    sett.pressure = 10
    sett.KMCEngine.name = 'ZacRos'
    sett.KMCEngine.path = './'
    sett.KMCOutput.path = './tests'
    sett.snapshots = ('time', 5.e-4)
    sett.process_statistics = ('time', 5.e-4)
    sett.species_numbers = ('time', 5.e-4)
    sett.event_report = 'off'
    sett.max_steps = 'infinity'
    sett.max_time = 250.0
    sett.wall_time = 3

    myJob = KMCJob(lattice=myLattice,
                   mechanism=myMechanism)


def test_pyzacros_example():
    """Assert input files."""
    pyzacros_example()
    list_of_files = ["lattice_input.dat",
                     "mechanism_input.dat"]
    for ij in list_of_files:
        f = open("tests/"+ij, "r")
        f_original = open("tests/original_inputs/RKFLoader/"+ij, "r")
        assert (f.read() == f_original.read())
    return
