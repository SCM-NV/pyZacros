#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import os
import sys
import shutil

from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.Mechanism import Mechanism
from pyzacros.classes.RKFLoader import RKFLoader
from pyzacros.classes.KMCJob import KMCJob

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

    if( job.ok() ):
        dirpath = os.path.dirname( results.rkfpath() )
        shutil.rmtree( RUNDIR+"/tests/test_RKFLoader.data/ProcessSearch-EON", ignore_errors=True )
        shutil.copytree( dirpath, RUNDIR+"/tests/test_RKFLoader.data/ProcessSearch-EON" )
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

    settings.input.ams.EON.EnergyLandscape.Load = RUNDIR+"/tests/test_RKFLoader.data/ProcessSearch-EON/ams.rkf"
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

    job = scm.plams.AMSJob(molecule=molecule, settings=settings, name="BindingSites-EON")
    results = job.run()

    if( job.ok() ):
        dirpath = os.path.dirname( results.rkfpath() )
        shutil.rmtree( RUNDIR+"/tests/test_RKFLoader.data/BindingSites-EON", ignore_errors=True )
        shutil.copytree( dirpath, RUNDIR+"/tests/test_RKFLoader.data/BindingSites-EON" )
    else:
        raise Exception( "Binding sites calculation FAILED!" )

    scm.plams.finish()

    return results


def test_RKFLoader():
    global RUNDIR
    RUNDIR = os.getcwd()

    """Test of the Mechanism class loaded from AMS."""
    print( "---------------------------------------------------" )
    print( ">>> Testing RKFLoader class" )
    print( "---------------------------------------------------" )

    # Tries to use PLAMS from AMS
    AMSHOME = os.getenv("AMSHOME")
    if( AMSHOME is not None ):
        if( AMSHOME+"/scripting" not in sys.path ):
            sys.path.append( AMSHOME+"/scripting" )

            # If AMS is available. It runs the calculations to generate
            # both the energy landscape and binding sites. Results are
            # saved in the directory tests/test_RKFLoader.data
            results = buildEnergyLandscape()
            results = deriveBindingSites()

    # If AMS is not available, it tries to load the package from PYTHONPATH
    try:
        import scm.plams
    except ImportError:
        raise Exception( "Package scm.plams is required!" )


    # Results are loaded from tests/test_RKFLoader.data
    scm.plams.init()
    job = scm.plams.AMSJob.load_external( path="tests/test_RKFLoader.data/BindingSites-EON" )
    scm.plams.finish()

    myRKFLoader = RKFLoader( job.results )

    output  = str( myRKFLoader.mechanism )+"\n"
    myRKFLoader.lattice.repeat_cell = [2,2]
    output += str( myRKFLoader.lattice )

    print(output)

    #myJob = KMCJob( myRKFLoader.mechanism )
    #myJob.writeInputFiles()

    expectedOutput = """\
mechanism
reversible_step O1*-B,*-A:(1,2)<-->*-B,O1*-A:(1,2)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types B A
  pre_expon 1.00000e+13
  pe_ratio 0.67600
  activ_eng 0.50150
end_step
end_mechanism
lattice periodic_cell
cell_vectors
  8.31558  0.00000
  4.15779  7.20150
repeat_cell 2 2
n_cell_sites 18
n_site_types 2
site_type_names A B
site_types B B B B B B B B B A A A A A A A A A
site_coordinates
  8.31494  6.40181
  11.08744  6.40143
  5.54295  1.60256
  2.77150  1.60206
  8.31489  1.60173
  9.70139  4.00310
  5.54313  6.40167
  6.92898  4.00292
  4.15719  4.00286
  8.31502  3.20297
  1.38524  0.80196
  2.77189  3.20341
  6.92937  0.80200
  5.54298  3.20318
  4.15691  0.80241
  6.92874  5.60174
  9.70124  5.60128
  4.15701  5.60169
neighboring_structure
  6-10 self
  11-4 self
  11-5 east
  13-2 north
  10-8 self
  9-12 self
  13-3 self
  5-13 self
  1-15 north
  6-12 east
  14-9 self
  15-3 self
  4-15 self
  8-14 self
  10-5 self
  11-7 north
  7-16 self
  2-18 east
  17-6 self
  17-1 self
  16-8 self
  14-3 self
  12-4 self
  2-17 self
  16-1 self
  18-9 self
  18-7 self
end_neighboring_structure
end_lattice\
"""
    assert( output == expectedOutput )

