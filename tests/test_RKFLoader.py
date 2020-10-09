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
from pyzacros.utils.compareReports import *


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
            #results = buildEnergyLandscape()
            #results = deriveBindingSites()

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
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.5014956703374196
end_reversible_step
end_mechanism
lattice periodic_cell
cell_vectors
  8.31557575  0.00000000
  4.15778787  7.20149984
repeat_cell 2 2
n_cell_sites 18
n_site_types 2
site_type_names A B
site_types B B B B B B B B B A A A A A A A A A
site_coordinates
  0.55544631  0.88895506
  0.88888281  0.88890194
  0.55531418  0.22252584
  0.22205914  0.22246160
  0.88870894  0.22241668
  0.88871756  0.55587026
  0.22212838  0.88893607
  0.55532980  0.55584586
  0.22200935  0.55583722
  0.77755064  0.44476415
  0.11090367  0.11136053
  0.11092413  0.44482603
  0.77761765  0.11136525
  0.44418100  0.44479399
  0.44418302  0.11142222
  0.44429648  0.77785687
  0.77773815  0.77779297
  0.11098086  0.77785015
neighboring_structure
  10-6 self
  4-11 self
  5-11 east
  2-13 north
  8-10 self
  12-9 self
  3-13 self
  13-5 self
  1-15 north
  6-12 east
  9-14 self
  3-15 self
  15-4 self
  14-8 self
  5-10 self
  7-11 north
  16-7 self
  2-18 east
  6-17 self
  1-17 self
  8-16 self
  3-14 self
  4-12 self
  17-2 self
  1-16 self
  9-18 self
  7-18 self
end_neighboring_structure
end_lattice\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )
