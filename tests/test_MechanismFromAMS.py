#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import os
import sys

from pyzacros.classes.Species import Species
from pyzacros.classes.SpeciesList import SpeciesList
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.Mechanism import Mechanism

def test_MechanismFromAMS():
    """Test of the Mechanism class loaded from AMS."""
    print( "---------------------------------------------------" )
    print( ">>> Testing AMSResultsLoader class" )
    print( "---------------------------------------------------" )

    AMSHOME = os.getenv("AMSHOME")
    if( AMSHOME is not None ):
        if( AMSHOME+"/scripting" not in sys.path ): sys.path.append( AMSHOME+"/scripting" )

        try:
            import scm.plams
        except ImportError:
            pass

        scm.plams.init()

        molecule = scm.plams.Molecule( "tests/4H2O.xyz" )

        settings = scm.plams.Settings()
        settings.input.ams.Task = 'BasinHopping-EON'
        settings.input.MOPAC
        settings.input.ams.Properties.NormalModes = "T"

        settings.input.ams.EON.RandomSeed = 100
        settings.input.ams.EON.Temperature = 400.0
        settings.input.ams.EON.SamplingFreq = "Full"

        settings.input.ams.EON.BasinHopping.Steps = 10
        settings.input.ams.EON.BasinHopping.Displacement = 1.0
        settings.input.ams.EON.BasinHopping.WriteUnique = "T"

        settings.input.ams.EON.Optimizer.Method = "CG"
        settings.input.ams.EON.Optimizer.ConvergedForce = 0.01
        settings.input.ams.EON.Optimizer.MaxIterations = 300

        settings.input.ams.EON.StructureComparison.DistanceDifference = 0.1
        settings.input.ams.EON.StructureComparison.NeighborCutoff = 7.6
        settings.input.ams.EON.StructureComparison.CheckRotation = "T"
        settings.input.ams.EON.StructureComparison.IndistinguishableAtoms = "T"
        settings.input.ams.EON.StructureComparison.EnergyDifference = 0.01
        settings.input.ams.EON.StructureComparison.RemoveTranslation = "T"

        job1 = scm.plams.AMSJob(molecule=molecule, settings=settings, name='BasinHopping')
        print( job1.get_input() )
        results = job1.run()

        settings.input.ams.Task = 'NudgedElasticBand-EON'
        settings.input.ams.EON.LoadStates.File = results.rkfpath()

        job2 = job1
        job2 = scm.plams.AMSJob(molecule=molecule, settings=settings, name='NudgedElasticBand')
        print( job2.get_input() )
        results = job2.run()

        myMechanism = Mechanism()
        myMechanism.fromAMS( results )

        print( myMechanism )

        scm.plams.finish()

test_MechanismFromAMS()
