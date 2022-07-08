import os
import sys
import shutil

import scm.plams

import pyzacros as pz
from pyzacros.utils.compareReports import compare

RUNDIR=None

def generateAMSResults():
    """Generates of the energy landscape for the O-Pt111 system"""

    sett_ads = scm.plams.Settings()
    sett_ads.input.ams.Task = "PESExploration"
    sett_ads.input.ams.PESExploration.Job = 'ProcessSearch'
    sett_ads.input.ams.PESExploration.RandomSeed = 100
    sett_ads.input.ams.PESExploration.NumExpeditions = 10
    sett_ads.input.ams.PESExploration.NumExplorers = 4
    sett_ads.input.ams.PESExploration.Optimizer.ConvergedForce = 0.005
    sett_ads.input.ams.PESExploration.SaddleSearch.ZeroModeAbortCurvature = 0.0001
    sett_ads.input.ams.PESExploration.SaddleSearch.MinEnergyBarrier = 0.02
    sett_ads.input.ams.PESExploration.SaddleSearch.MaxEnergy = 4.0
    sett_ads.input.ams.PESExploration.DynamicSeedStates = 'T'
    sett_ads.input.ams.PESExploration.StructureComparison.DistanceDifference = 0.2
    sett_ads.input.ams.PESExploration.StructureComparison.NeighborCutoff = 2.4
    sett_ads.input.ams.PESExploration.StructureComparison.EnergyDifference = 0.05
    sett_ads.input.ams.PESExploration.CalculateFragments = 'T'
    sett_ads.input.ams.PESExploration.StructureComparison.CheckSymmetry = 'T'
    sett_ads.input.ams.PESExploration.BindingSites.Calculate = 'T'
    sett_ads.input.ams.PESExploration.BindingSites.NeighborCutoff = 3.8
    sett_ads.input.ams.PESExploration.BindingSites.DistanceDifference = 0.5
    sett_ads.input.ams.PESExploration.StatesAlignment.ReferenceRegion = 'surface'
    sett_ads.input.ReaxFF.ForceField = 'CHONSFPtClNi.ff'
    sett_ads.input.ReaxFF.Charges.Solver = 'Direct'
    sett_ads.input.ams.Constraints.FixedRegion = 'surface'
    sett_ads.input.ams.PESPointCharacter.NegativeEigenvalueTolerance = -0.001

    sett_lat = sett_ads.copy()
    sett_lat.input.ams.PESExploration.Job = 'LandscapeRefinement'
    sett_lat.input.ams.PESExploration.LoadEnergyLandscape.GenerateSymmetryImages = 'T'
    sett_lat.input.ams.PESExploration.SaddleSearch.RelaxFromSaddlePoint = 'T'
    sett_lat.input.ams.GeometryOptimization.InitialHessian.Type = 'Calculate'
    sett_lat.input.ams.PESExploration.StructureComparison.CheckSymmetry = 'F'

    molO = scm.plams.Molecule( "tests/O-Pt111.xyz" )
    molCO = scm.plams.Molecule( "tests/CO-Pt111.xyz" )

    jobO_ads = scm.plams.AMSJob(molecule=molO, settings=sett_ads, name="O_ads-Pt111")
    jobCO_ads = scm.plams.AMSJob(molecule=molCO, settings=sett_ads, name="CO_ads-Pt111")

    sett_lat.input.ams.PESExploration.LoadEnergyLandscape.Path= '../O_ads-Pt111'
    jobO_lat = scm.plams.AMSJob(molecule=molO, settings=sett_lat, name="O-Pt111", depend=[jobO_ads])

    sett_lat.input.ams.PESExploration.LoadEnergyLandscape.Path= '../CO_ads-Pt111'
    jobCO_lat = scm.plams.AMSJob(molecule=molCO, settings=sett_lat, name="CO-Pt111", depend=[jobCO_ads])

    jobs = [ jobO_ads, jobCO_ads, jobO_lat, jobCO_lat ]

    for job in jobs:
        job.run()

    success = True
    for job in jobs:
        if not job.ok() and "AMSBIN" not in os.environ:
            print( "Warning: The calculation FAILED likely because AMS executable is not available!" )
            print( "         For testing purposes, now we load precalculated results.")
            success = False

    if success:
        scm.plams.delete_job( jobO_ads )
        scm.plams.delete_job( jobCO_ads )
    else:
        jobO_lat = scm.plams.load( RUNDIR+"/tests/test_RKFLoader.data/O-Pt111/O-Pt111.dill" )
        jobCO_lat = scm.plams.load( RUNDIR+"/tests/test_RKFLoader.data/CO-Pt111/CO-Pt111.dill" )

    return jobO_lat.results,jobCO_lat.results


def test_RKFLoader():
    """Test of the Mechanism class loaded from AMS."""
    global RUNDIR
    RUNDIR = os.getcwd()

    print( "---------------------------------------------------" )
    print( ">>> Testing RKFLoader class" )
    print( "---------------------------------------------------" )

    scm.plams.init(folder='test_RKFLoader')

    resultsO,resultsCO = generateAMSResults()

    scm.plams.finish()

    loaderO = pz.RKFLoader( resultsO )
    loaderCO = pz.RKFLoader( resultsCO )

    loader = pz.RKFLoader.merge( [loaderO, loaderCO] )
    loader.replace_site_types( ['N3333', 'N3334', 'N2222'], ['fcc', 'hcp', 'br'] )

    output  = str( loader.clusterExpansion )+"\n\n"
    output += str( loader.mechanism )+"\n\n"

    loader.lattice.set_repeat_cell( [2,2] )
    loader.lattice.plot( pause=2 )

    output += str( loader.lattice )

    print(output)

    expectedOutput = """\
energetics

cluster O*-fcc
  sites 1
  lattice_state
    1 O* 1
  site_types fcc
  graph_multiplicity 1
  cluster_eng -1.98060e+02
end_cluster

cluster O*-hcp
  sites 1
  lattice_state
    1 O* 1
  site_types hcp
  graph_multiplicity 1
  cluster_eng -1.98060e+02
end_cluster

cluster CO*-fcc
  sites 1
  lattice_state
    1 CO* 1
  site_types fcc
  graph_multiplicity 1
  cluster_eng -2.08212e+02
end_cluster

cluster CO*-hcp
  sites 1
  lattice_state
    1 CO* 1
  site_types hcp
  graph_multiplicity 1
  cluster_eng -2.08212e+02
end_cluster

cluster CO*-br
  sites 1
  lattice_state
    1 CO* 1
  site_types br
  graph_multiplicity 1
  cluster_eng -2.08212e+02
end_cluster

end_energetics

mechanism

reversible_step O*_1-hcp,*_2-fcc<-->*_1-hcp,O*_2-fcc;(0,1)
  sites 2
  neighboring 1-2
  initial
    1 * 1
    2 O* 1
  final
    1 O* 1
    2 * 1
  site_types hcp fcc
  pre_expon  1.92044e+13
  pe_ratio  1.11482e+00
  activ_eng  7.00299e-01
end_reversible_step

reversible_step O*_1-fcc,*_2-hcp<-->*_1-fcc,O*_2-hcp;(0,1)
  sites 2
  neighboring 1-2
  initial
    1 O* 1
    2 * 1
  final
    1 * 1
    2 O* 1
  site_types fcc hcp
  pre_expon  1.92044e+13
  pe_ratio  1.11482e+00
  activ_eng  7.00299e-01
end_reversible_step

step *-fcc:O-->O*-fcc
  gas_reacs_prods O -1
  sites 1
  initial
    1 * 1
  final
    1 O* 1
  site_types fcc
  pre_expon  1.06511e+07
  activ_eng  0.00000e+00
end_step

step *-hcp:O-->O*-hcp
  gas_reacs_prods O -1
  sites 1
  initial
    1 * 1
  final
    1 O* 1
  site_types hcp
  pre_expon  1.06511e+07
  activ_eng  0.00000e+00
end_step

reversible_step CO*_1-hcp,*_2-br<-->*_1-hcp,CO*_2-br;(0,1)
  sites 2
  neighboring 1-2
  initial
    1 CO* 1
    2 * 1
  final
    1 * 1
    2 CO* 1
  site_types hcp br
  pre_expon  1.56321e+13
  pe_ratio  6.96720e+00
  activ_eng  7.89789e-01
end_reversible_step

reversible_step CO*_1-fcc,*_2-br<-->*_1-fcc,CO*_2-br;(0,1)
  sites 2
  neighboring 1-2
  initial
    1 CO* 1
    2 * 1
  final
    1 * 1
    2 CO* 1
  site_types fcc br
  pre_expon  1.57076e+13
  pe_ratio  7.04305e+00
  activ_eng  7.94883e-01
end_reversible_step

step *-fcc:CO-->CO*-fcc
  gas_reacs_prods CO -1
  sites 1
  initial
    1 * 1
  final
    1 CO* 1
  site_types fcc
  pre_expon  8.05092e+06
  activ_eng  0.00000e+00
end_step

step *-hcp:CO-->CO*-hcp
  gas_reacs_prods CO -1
  sites 1
  initial
    1 * 1
  final
    1 CO* 1
  site_types hcp
  pre_expon  8.05092e+06
  activ_eng  0.00000e+00
end_step

step *-br:CO-->CO*-br
  gas_reacs_prods CO -1
  sites 1
  initial
    1 * 1
  final
    1 CO* 1
  site_types br
  pre_expon  8.05092e+06
  activ_eng  0.00000e+00
end_step

end_mechanism

lattice explicit
  cell_vectors
  8.31557575  0.00000000
  4.15778787  7.20149984
  n_sites 63
  max_coord 3
  n_site_types 3
  site_type_names br fcc hcp
  lattice_structure
       1       0.92536450       0.55407768         hcp     1     2
       2       2.31078110       1.35400928         fcc     3     1     3     4
       3       2.31129379       2.95457763         hcp     2     2     5
       4       3.69722308       0.55407768         hcp     2     2     7
       5       3.69671039       3.75450923         fcc     3     3     6     8
       6       3.69722308       5.35507757         hcp     2     9     5
       7       5.08263968       1.35400928         fcc     3    10     4     8
       8       5.08315237       2.95457763         hcp     3    11     5     7
       9       5.08263968       6.15500917         fcc     2    12     6
      10       6.46908166       0.55407768         hcp     2    13     7
      11       6.46856897       3.75450923         fcc     3    12    14     8
      12       6.46908166       5.35507757         hcp     3     9    11    15
      13       7.85449826       1.35400928         fcc     2    10    14
      14       7.85501095       2.95457763         hcp     3    11    13    16
      15       7.85449826       6.15500917         fcc     2    17    12
      16       9.24042755       3.75450923         fcc     2    17    14
      17       9.24094024       5.35507757         hcp     3    18    15    16
      18      10.62635684       6.15500917         fcc     1    17
      19       0.92565822       0.55493308         hcp     1    37
      20       2.31110273       1.35413312         fcc     3    37    38    39
      21       2.31158751       2.95543303         hcp     2    38    40
      22       3.69751680       0.55493308         hcp     2    42    39
      23       3.69703202       3.75463307         fcc     3    41    43    40
      24       3.69751680       5.35593297         hcp     2    41    44
      25       5.08296131       1.35413312         fcc     3    42    45    47
      26       5.08344609       2.95543303         hcp     3    43    45    48
      27       5.08296131       6.15513301         fcc     3    49    44    46
      28       6.46937538       0.55493308         hcp     2    51    47
      29       6.46889060       3.75463307         fcc     3    50    52    48
      30       6.46937538       5.35593297         hcp     3    49    50    53
      31       7.85481989       1.35413312         fcc     3    51    54    56
      32       7.85530467       2.95543303         hcp     3    57    52    54
      33       7.85481989       6.15513301         fcc     3    58    53    55
      34       9.24074918       3.75463307         fcc     3    57    59    60
      35       9.24123396       5.35593297         hcp     3    58    59    61
      36      10.62667847       6.15513301         fcc     3    61    62    63
      37       1.60609631       0.94695596          br     2    19    20
      38       2.31093302       2.16819424          br     2    20    21
      39       3.01601528       0.94695595          br     2    20    22
      40       2.99202560       3.34745591          br     2    21    23
      41       3.69686230       4.56869419          br     2    23    24
      42       4.37795489       0.94695595          br     2    25    22
      43       4.40194457       3.34745590          br     2    26    23
      44       4.37795489       5.74795584          br     2    27    24
      45       5.08279160       2.16819424          br     2    25    26
      46       5.08279159       6.96919413          br     1    27
      47       5.78787386       0.94695595          br     2    25    28
      48       5.76388418       3.34745591          br     2    26    29
      49       5.78787386       5.74795584          br     2    27    30
      50       6.46872089       4.56869419          br     2    29    30
      51       7.14981347       0.94695596          br     2    28    31
      52       7.17380315       3.34745590          br     2    29    32
      53       7.14981347       5.74795584          br     2    33    30
      54       7.85465018       2.16819424          br     2    31    32
      55       7.85465017       6.96919413          br     1    33
      56       8.55973244       0.94695594          br     1    31
      57       8.53574276       3.34745591          br     2    34    32
      58       8.55973244       5.74795584          br     2    33    35
      59       9.24057947       4.56869419          br     2    34    35
      60       9.94566174       3.34745590          br     1    34
      61       9.92167205       5.74795585          br     2    35    36
      62      10.62650876       6.96919413          br     1    36
      63      11.33159102       5.74795583          br     1    36
  end_lattice_structure
end_lattice\
"""
    assert( compare( output, expectedOutput, rel_error=0.1 ) )
