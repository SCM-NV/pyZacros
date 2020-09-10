#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests of the pyZacros classes."""

import os
import sys
import shutil

from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.Mechanism import Mechanism
from pyzacros.classes.RKFLoader import RKFLoader

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

    if( results.ok() ):
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

    output = str( myRKFLoader.mechanism )
    expectedOutput = """\
mechanism
reversible_step *-11,O1*-11:(2,1)<-->O1*-11,*-11:(2,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.018429619263367947
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.025712675062943724
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.025717182279094253
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.025730351781071192
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.025698309562196542
end_step
reversible_step *-11,O1*-11:(2,1)<-->O1*-11,*-11:(2,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.018431176700345553
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.02573258826702851
end_step
reversible_step *-11,O1*-11:(2,1)<-->O1*-11,*-11:(2,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.018431982078470632
end_step
reversible_step *-11,O1*-11:(2,1)<-->O1*-11,*-11:(2,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.01841684445719327
end_step
reversible_step *-11,O1*-11:(2,1)<-->O1*-11,*-11:(2,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.018438751784363383
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.02570200659150146
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.025744220437390553
end_step
reversible_step *-11,O1*-11:(2,1)<-->O1*-11,*-11:(2,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.018426524078024364
end_step
reversible_step *-11,O1*-11:(2,1)<-->O1*-11,*-11:(2,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.018436120935394484
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.025744186940190872
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.02573415807260382
end_step
reversible_step *-11,O1*-11:(2,1)<-->O1*-11,*-11:(2,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.01842521392860963
end_step
reversible_step *-11,O1*-11:(2,1)<-->O1*-11,*-11:(2,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.018420239435744
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.02574598069616041
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.025779906824526577
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.025734297422976837
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.025765224531051345
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.02577819379800861
end_step
reversible_step *-11,O1*-11:(2,1)<-->O1*-11,*-11:(2,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.01844367850018802
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.02579921286374809
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.02574558252983916
end_step
reversible_step O1*-11,*-11:(1,2)<-->*-11,O1*-11:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 O1* 1
    2 * 1
  final
    1 * 1
    2 O1* 1
  site_types 11 15
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.025774060719184533
end_step
end_mechanism\
"""
    assert( output == expectedOutput )


test_RKFLoader()
