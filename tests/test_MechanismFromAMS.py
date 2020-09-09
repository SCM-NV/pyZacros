#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import os
import sys
import shutil

from pyzacros.classes.Species import Species
from pyzacros.classes.SpeciesList import SpeciesList
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.Mechanism import Mechanism

RUNDIR=None

def buildEnergyLandscape():
    """Generates of the energy landscape for the O-Pt111 system"""
    import scm.plams

    scm.plams.init()

    molecule = scm.plams.Molecule( "tests/O-Pt111.xyz" )

    for atom in molecule:
        if( atom.symbol == "O" ):
            atom.properties.suffix = "region=adsorbate"
        else:
            atom.properties.suffix = "region=surface"

    settings = scm.plams.Settings()
    settings.input.ams.Task = "ProcessSearch-EON"

    settings.input.ams.Constraints.FixedRegion = "surface"

    settings.input.ams.EON.RandomSeed = 100
    settings.input.ams.EON.SamplingFreq = "Normal"
    settings.input.ams.EON.NumJobs = 150
    settings.input.ams.EON.DynamicSeedStates = True

    settings.input.ams.EON.SaddleSearch.MinModeMethod = "dimer"
    settings.input.ams.EON.SaddleSearch.DisplaceRadius = 4.0
    settings.input.ams.EON.SaddleSearch.DisplaceMagnitude = 0.01
    settings.input.ams.EON.SaddleSearch.MaxEnergy = 2.0

    settings.input.ams.EON.Optimizer.Method = "CG"
    settings.input.ams.EON.Optimizer.ConvergedForce = 0.001
    settings.input.ams.EON.Optimizer.MaxIterations = 2000

    settings.input.ams.EON.StructureComparison.DistanceDifference = 0.1
    settings.input.ams.EON.StructureComparison.NeighborCutoff = 10.0
    settings.input.ams.EON.StructureComparison.CheckRotation = False
    settings.input.ams.EON.StructureComparison.IndistinguishableAtoms = True
    settings.input.ams.EON.StructureComparison.EnergyDifference = 0.01
    settings.input.ams.EON.StructureComparison.RemoveTranslation = True

    settings.input.ReaxFF
    settings.input.ReaxFF.ForceField = "CHONSFPtClNi.ff"
    settings.input.ReaxFF.Charges.Converge.Charge = 1e-12

    job = scm.plams.AMSJob(molecule=molecule, settings=settings, name="ProcessSearch-EON")
    results = job.run()

    if( results.ok() ):
        dirpath = os.path.dirname( results.rkfpath() )
        shutil.rmtree( RUNDIR+"/tests/test_MechanismFromAMS.data/ProcessSearch-EON", ignore_errors=True )
        shutil.copytree( dirpath, RUNDIR+"/tests/test_MechanismFromAMS.data/ProcessSearch-EON" )
    else:
        raise Exception( "Energy landscape calculation FAILED!" )

    scm.plams.finish()

    return results


def deriveBindingSites():
    """Derives the binding sites from the previously calculated energy landscape"""
    import scm.plams

    scm.plams.init()

    molecule = scm.plams.Molecule( "tests/O-Pt111.xyz" )

    for atom in molecule:
        if( atom.symbol == "O" ):
            atom.properties.suffix = "region=adsorbate"
        else:
            atom.properties.suffix = "region=surface"

    settings = scm.plams.Settings()
    settings.input.ams.Task = "BindingSites-EON"

    settings.input.ams.Constraints.FixedRegion = "surface"

    settings.input.ams.EON.EnergyLandscape.Load = RUNDIR+"/tests/test_MechanismFromAMS.data/ProcessSearch-EON/ams.rkf"
    settings.input.ams.EON.EnergyLandscape.Adsorbate = "adsorbate"

    settings.input.ams.EON.BindingSites.DistanceDifference = 5.0
    settings.input.ams.EON.BindingSites.AllowDisconnected = False
    #settings.input.ams.EON.BindingSites.LatticeScaleFactors = [ 3, 3, 1 ]  ! @TODO it is not working

    settings.input.ams.EON.StructureComparison.DistanceDifference = 0.1
    settings.input.ams.EON.StructureComparison.NeighborCutoff = 10.0
    settings.input.ams.EON.StructureComparison.CheckRotation = False
    settings.input.ams.EON.StructureComparison.IndistinguishableAtoms = True
    settings.input.ams.EON.StructureComparison.EnergyDifference = 0.1
    settings.input.ams.EON.StructureComparison.RemoveTranslation = True

    settings.input.ReaxFF
    settings.input.ReaxFF.ForceField = "CHONSFPtClNi.ff"
    settings.input.ReaxFF.Charges.Converge.Charge = 1e-12

    settings.input.ams.Properties.NormalModes = True
    #settings.input.ams.Thermo

    job = scm.plams.AMSJob(molecule=molecule, settings=settings, name="BindingSites-EON")
    results = job.run()

    if( results.ok() ):
        dirpath = os.path.dirname( results.rkfpath() )
        shutil.rmtree( RUNDIR+"/tests/test_MechanismFromAMS.data/BindingSites-EON", ignore_errors=True )
        shutil.copytree( dirpath, RUNDIR+"/tests/test_MechanismFromAMS.data/BindingSites-EON" )
    else:
        raise Exception( "Binding sites calculation FAILED!" )

    scm.plams.finish()

    return results


def test_MechanismFromAMS():
    global RUNDIR
    RUNDIR = os.getcwd()

    """Test of the Mechanism class loaded from AMS."""
    print( "---------------------------------------------------" )
    print( ">>> Testing AMSResultsLoader class" )
    print( "---------------------------------------------------" )

    # Tries to use PLAMS from AMS
    AMSHOME = os.getenv("AMSHOME")
    if( AMSHOME is not None ):
        if( AMSHOME+"/scripting" not in sys.path ):
            sys.path.append( AMSHOME+"/scripting" )

            # If AMS is available. It runs the calculations to generate
            # both the energy landscape and binding sites. Results are
            # saved in the directory tests/test_MechanismFromAMS.data
            #results = buildEnergyLandscape()
            #results = deriveBindingSites()

    # If AMS is not available, it tries to load the package from PYTHONPATH
    try:
        import scm.plams
    except ImportError:
        raise Exception( "Package scm.plams is required!" )

    scm.plams.init()

    # Results are loaded from tests/test_MechanismFromAMS.data
    job = scm.plams.AMSJob.load_external( path="tests/test_MechanismFromAMS.data/BindingSites-EON" )

    myMechanism = Mechanism()
    myMechanism.fromAMS( job.results )

    #print( myMechanism )

    scm.plams.finish()


test_MechanismFromAMS()
