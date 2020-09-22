#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.utils.compareReports import *


def test_KMCSettings():
    """Test of the KMCSettings class."""
    print("---------------------------------------------------")
    print(">>> Testing KMCSettings class")
    print("---------------------------------------------------")

    # Adsorbed specie
    sett = KMCSettings()
    sett.simulation_input.random_seed = 71543
    sett.simulation_input.temperature = 380.0
    sett.simulation_input.pressure = 2.00
    sett.simulation_input.snapshots_on_time = 1e-5
    sett.simulation_input.process_statistics_on_time = 1e-5
    sett.simulation_input.species_numbers_on_time = 1e-5
    sett.simulation_input.event_report_on = 20
    sett.simulation_input.max_steps = "infinity"
    sett.simulation_input.max_time = 1.0e+50
    sett.simulation_input.wall_time = 5000
    output = str(sett)
    expectedOutput = """\
simulation_input: \t
                 random_seed: \t71543
                 temperature: \t380.0
                 pressure: \t2.0
                 snapshots_on_time: \t1e-05
                 process_statistics_on_time: \t1e-05
                 species_numbers_on_time: \t1e-05
                 event_report_on: \t20
                 max_steps: \tinfinity
                 max_time: \t1e+50
                 wall_time: \t5000
\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )
