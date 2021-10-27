import os
import sys
import shutil

import scm.plams

import pyzacros as pz
from pyzacros.utils.compareReports import compare

RUNDIR=None

def buildEnergyLandscape():
    """Generates of the energy landscape for the O-Pt111 system"""
    scm.plams.init()

    molecule = scm.plams.Molecule( "tests/O-Pt111.xyz" )

    for atom in molecule:
        if( atom.symbol == "O" ):
            atom.properties.suffix = "region=adsorbate"
        else:
            atom.properties.suffix = "region=surface"

    settings = scm.plams.Settings()
    settings.input.ams.Task = "PESExploration"

    settings.input.ams.Constraints.FixedRegion = "surface"

    settings.input.ams.PESExploration.Job = "ProcessSearch"
    settings.input.ams.PESExploration.RandomSeed = 100
    settings.input.ams.PESExploration.NumExpeditions = 50
    settings.input.ams.PESExploration.NumExplorers = 5
    settings.input.ams.PESExploration.DynamicSeedStates = True
    settings.input.ams.PESExploration.Optimizer.ConvergedForce = 0.0001
    settings.input.ams.PESExploration.SaddleSearch.MaxEnergy = 2.0
    settings.input.ams.PESExploration.StructureComparison.DistanceDifference = 0.1
    settings.input.ams.PESExploration.StructureComparison.NeighborCutoff = 10.0
    settings.input.ams.PESExploration.StructureComparison.EnergyDifference = 0.01

    settings.input.ReaxFF
    settings.input.ReaxFF.ForceField = "CHONSFPtClNi.ff"
    settings.input.ReaxFF.Charges.Solver = "direct"

    job = scm.plams.AMSJob(molecule=molecule, settings=settings, name="PESExploration")
    results = job.run()

    if( not job.ok() ):
        print( "Warning: The EnergyLandscape calculation FAILED likely because AMS executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        job = scm.plams.load( RUNDIR+"/tests/test_RKFLoader.data/PESExploration/PESExploration.dill" )
        results = job.results

    scm.plams.finish()

    return results


def deriveBindingSites():
    """Derives the binding sites from the previously calculated energy landscape"""
    scm.plams.init()

    molecule = scm.plams.Molecule( "tests/O-Pt111.xyz" )

    for atom in molecule:
        if( atom.symbol == "O" ):
            atom.properties.suffix = "region=adsorbate"
        else:
            atom.properties.suffix = "region=surface"

    settings = scm.plams.Settings()
    settings.input.ams.Task = "PESExploration"

    settings.input.ams.Constraints.FixedRegion = "surface"

    settings.input.ams.PESExploration.Job = "BindingSites"
    settings.input.ams.PESExploration.LoadEnergyLandscape.Path = RUNDIR+"/tests/test_RKFLoader.data/PESExploration/ams.rkf"
    settings.input.ams.PESExploration.StatesAlignment.ReferenceRegion = "surface"
    settings.input.ams.PESExploration.StructureComparison.DistanceDifference = 0.1
    settings.input.ams.PESExploration.StructureComparison.NeighborCutoff = 3.5
    settings.input.ams.PESExploration.StructureComparison.EnergyDifference = 0.1

    settings.input.ReaxFF
    settings.input.ReaxFF.ForceField = "CHONSFPtClNi.ff"
    settings.input.ReaxFF.Charges.Solver = "direct"

    job = scm.plams.AMSJob(molecule=molecule, settings=settings, name="BindingSites")
    results = job.run()

    if( not job.ok() ):
        print( "Warning: The BindingSites calculation FAILED likely because AMS executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        job = scm.plams.load( RUNDIR+"/tests/test_RKFLoader.data/BindingSites/BindingSites.dill" )
        results = job.results

    scm.plams.finish()

    return results


def test_RKFLoader():
    """Test of the Mechanism class loaded from AMS."""
    global RUNDIR
    RUNDIR = os.getcwd()

    print( "---------------------------------------------------" )
    print( ">>> Testing RKFLoader class" )
    print( "---------------------------------------------------" )

    resultsEnergyLandscape = buildEnergyLandscape()
    resultsBindingSites = deriveBindingSites()

    myRKFLoader = pz.RKFLoader( resultsBindingSites )

    output  = str( myRKFLoader.mechanism )+"\n"
    myRKFLoader.lattice.set_repeat_cell( [2,2] )
    myRKFLoader.lattice.plot( pause=2 )
    output += str( myRKFLoader.lattice )

    print(output)

    expectedOutput = """\
mechanism

reversible_step O1*_0-B,*_1-A<-->*_0-B,O1*_1-A;(0,1)
  sites 2
  neighboring 2-1
  initial
    1 * 1
    2 O1* 1
  final
    1 O1* 1
    2 * 1
  site_types B A
  pre_expon 1.71991e+13
  pe_ratio 8.95976e-01
  activ_eng 5.01496e-01
end_reversible_step

end_mechanism
lattice periodic_cell
cell_vectors
  8.31557575  0.00000000
  4.15778787  7.20149984
repeat_cell 2 2
n_site_types 2
site_type_names A B
n_cell_sites 18
site_types B B B B B B B B B A A A A A A A A A
site_coordinates
  0.22205823  0.22246190
  0.22201007  0.55583761
  0.55530927  0.22253061
  0.22212815  0.88893597
  0.55532993  0.55584592
  0.88870872  0.22241805
  0.55544680  0.88895434
  0.88871779  0.55587041
  0.88888376  0.88890149
  0.11090282  0.11135927
  0.11092394  0.44482539
  0.44418381  0.11142280
  0.11097989  0.77785422
  0.44418388  0.44478701
  0.77761175  0.11136662
  0.44429985  0.77785242
  0.77755045  0.44476403
  0.77773905  0.77779245
neighboring_structure
  17-8 self
  1-10 self
  6-10 east
  9-15 north
  5-17 self
  2-11 self
  3-15 self
  15-6 self
  7-12 north
  8-11 east
  14-2 self
  3-12 self
  12-1 self
  14-5 self
  6-17 self
  4-10 north
  16-4 self
  9-13 east
  8-18 self
  7-18 self
  5-16 self
  3-14 self
  1-11 self
  18-9 self
  7-16 self
  2-13 self
  13-4 self
end_neighboring_structure
end_lattice\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )
