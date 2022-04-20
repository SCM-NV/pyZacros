import os
import sys
import shutil

import scm.plams

import pyzacros as pz
from pyzacros.utils.compareReports import compare

RUNDIR=None

def buildEnergyLandscape():
    """Generates of the energy landscape for the O-Pt111 system"""

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

    if( not job.ok() and "AMSBIN" not in os.environ ):
        print( "Warning: The EnergyLandscape calculation FAILED likely because AMS executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        job = scm.plams.load( RUNDIR+"/tests/test_RKFLoader.data/PESExploration/PESExploration.dill" )
        results = job.results

    return results


def deriveBindingSites(resultsEnergyLandscape):
    """Derives the binding sites from the previously calculated energy landscape"""

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
    settings.input.ams.PESExploration.LoadEnergyLandscape.Path = resultsEnergyLandscape.job.path
    settings.input.ams.PESExploration.StatesAlignment.ReferenceRegion = "surface"
    settings.input.ams.PESExploration.StructureComparison.DistanceDifference = 0.1
    settings.input.ams.PESExploration.StructureComparison.NeighborCutoff = 3.5
    settings.input.ams.PESExploration.StructureComparison.EnergyDifference = 0.1

    settings.input.ReaxFF
    settings.input.ReaxFF.ForceField = "CHONSFPtClNi.ff"
    settings.input.ReaxFF.Charges.Solver = "direct"

    job = scm.plams.AMSJob(molecule=molecule, settings=settings, name="BindingSites")
    results = job.run()

    if( not job.ok() and "AMSBIN" not in os.environ ):
        print( "Warning: The BindingSites calculation FAILED likely because AMS executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        job = scm.plams.load( RUNDIR+"/tests/test_RKFLoader.data/BindingSites/BindingSites.dill" )
        results = job.results

    return results


def test_RKFLoader():
    """Test of the Mechanism class loaded from AMS."""
    global RUNDIR
    RUNDIR = os.getcwd()

    print( "---------------------------------------------------" )
    print( ">>> Testing RKFLoader class" )
    print( "---------------------------------------------------" )

    scm.plams.init(folder='test_RKFLoader')

    resultsEnergyLandscape = buildEnergyLandscape()
    resultsBindingSites = deriveBindingSites(resultsEnergyLandscape)

    scm.plams.finish()

    myRKFLoader = pz.RKFLoader( resultsBindingSites )

    output  = str( myRKFLoader.mechanism )+"\n"
    myRKFLoader.lattice.set_repeat_cell( [2,2] )
    myRKFLoader.lattice.plot( pause=2 )
    output += str( myRKFLoader.lattice )

    print(output)

    expectedOutput = """\
mechanism

reversible_step O*_0-N6,*_1-N7<-->*_0-N6,O*_1-N7;(0,1)
  sites 2
  neighboring 2-1
  initial
    1 O* 1
    2 * 1
  final
    1 * 1
    2 O* 1
  site_types N6 N7
  pre_expon  1.91958e+13
  pe_ratio  1.11610e+00
  activ_eng  6.99109e-01
end_reversible_step

end_mechanism
lattice periodic_cell
  cell_vectors
    8.31557575    0.00000000
    4.15778787    7.20149984
  repeat_cell 2 2
  n_site_types 2
  site_type_names N6 N7
  n_cell_sites 18
  site_types N6 N6 N6 N6 N6 N6 N6 N6 N6 N7 N7 N7 N7 N7 N7 N7 N7 N7
  site_coordinates
    0.22205907    0.22246154
    0.22201017    0.55583759
    0.55530927    0.22253061
    0.22212824    0.88893590
    0.55532987    0.55584578
    0.88870959    0.22241692
    0.55544654    0.88895451
    0.88871815    0.55587070
    0.88888339    0.88890174
    0.11090285    0.11135931
    0.11092403    0.44482534
    0.44418361    0.11142266
    0.11097972    0.77785462
    0.44418449    0.44478609
    0.77761030    0.11136642
    0.44430025    0.77785231
    0.77755059    0.44476380
    0.77773862    0.77779425
  neighboring_structure
    8-17  self
    1-10  self
    6-10  east
    9-15  north
    5-17  self
    2-11  self
    3-15  self
    6-15  self
    7-12  north
    8-11  east
    2-14  self
    3-12  self
    1-12  self
    5-14  self
    6-17  self
    4-10  north
    4-16  self
    9-13  east
    8-18  self
    7-18  self
    5-16  self
    3-14  self
    1-11  self
    9-18  self
    7-16  self
    2-13  self
    4-13  self
  end_neighboring_structure
end_lattice\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )
