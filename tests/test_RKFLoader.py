import os
import sys
import shutil

import scm.plams

#import pyzacros as pz
#from pyzacros.utils.compareReports import compare

import scm.pyzacros as pz
from scm.pyzacros.utils.compareReports import compare

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
    sett_ads.input.ams.PESPointCharacter.NegativeFrequenciesTolerance = -30.0

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

    try:
        for job in jobs:
            job.run()

        for job in jobs:
            if not job.ok():
                raise scm.plams.JobError("Error: AMS calculation FAILED!")

        scm.plams.delete_job( jobO_ads )
        scm.plams.delete_job( jobCO_ads )

    except pz.ZacrosExecutableNotFoundError:

        print( "Warning: The calculation FAILED because the AMS executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

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

    loaderO.replace_site_types( ['N7', 'N9'], ['hcp', 'fcc'] )
    loaderCO.replace_site_types( ['N5', 'N6', 'N7'], ['br', 'fcc', 'hcp'] )

    loader = pz.RKFLoader.merge( [loaderO, loaderCO] )

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
  cluster_eng -3.27305e+00
end_cluster

cluster CO*-fcc
  sites 1
  lattice_state
    1 CO* 1
  site_types fcc
  graph_multiplicity 1
  cluster_eng -1.98377e+00
end_cluster

end_energetics

mechanism

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

reversible_step O*-fcc<-->*-fcc:O
  gas_reacs_prods O -1
  sites 1
  initial
    1 * 1
  final
    1 O* 1
  site_types fcc
  pre_expon  1.06511e+07
  pe_ratio  4.12763e-08
  activ_eng  0.00000e+00
end_reversible_step

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
  pre_expon  1.57255e+13
  pe_ratio  6.89981e+00
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
  pre_expon  1.56897e+13
  pe_ratio  6.96862e+00
  activ_eng  7.94880e-01
end_reversible_step

reversible_step CO*-fcc<-->*-fcc:CO
  gas_reacs_prods CO -1
  sites 1
  initial
    1 * 1
  final
    1 CO* 1
  site_types fcc
  pre_expon  8.05092e+06
  pe_ratio  2.58781e-16
  activ_eng  0.00000e+00
end_reversible_step

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
       1  2.31078110  1.35400928         fcc     3    10    11    12
       2  3.69671039  3.75450923         fcc     3    11    13    14
       3  5.08263968  1.35400928         fcc     3    12    14    15
       4  5.08263968  6.15500917         fcc     2    13    16
       5  6.46856897  3.75450923         fcc     3    17    14    16
       6  7.85449826  1.35400928         fcc     2    17    15
       7  7.85449826  6.15500917         fcc     2    18    16
       8  9.24042755  3.75450923         fcc     2    17    18
       9  10.62635684  6.15500917         fcc     1    18
      10  0.92536450  0.55407768         hcp     1     1
      11  2.31129379  2.95457763         hcp     2     1     2
      12  3.69722308  0.55407768         hcp     2     1     3
      13  3.69722308  5.35507757         hcp     2     2     4
      14  5.08315237  2.95457763         hcp     3     2     3     5
      15  6.46908166  0.55407768         hcp     2     3     6
      16  6.46908166  5.35507757         hcp     3     4     5     7
      17  7.85501095  2.95457763         hcp     3     5     6     8
      18  9.24094024  5.35507757         hcp     3     9     7     8
      19  0.92565822  0.55493308         hcp     1    37
      20  2.31054991  1.35381300         fcc     3    37    38    40
      21  2.31158751  2.95543303         hcp     2    38    39
      22  3.69751680  0.55493308         hcp     2    42    40
      23  3.69647920  3.75431295         fcc     3    41    44    39
      24  3.69751680  5.35593297         hcp     2    41    43
      25  5.08240849  1.35381300         fcc     3    42    45    48
      26  5.08344609  2.95543303         hcp     3    44    45    47
      27  5.08240849  6.15481289         fcc     3    49    43    46
      28  6.46937538  0.55493308         hcp     2    51    48
      29  6.46833778  3.75431295         fcc     3    50    53    47
      30  6.46937538  5.35593297         hcp     3    49    50    52
      31  7.85426707  1.35381300         fcc     3    57    51    54
      32  7.85426707  6.15481289         fcc     3    58    52    55
      33  7.85530467  2.95543303         hcp     3    53    54    56
      34  9.24019636  3.75431295         fcc     3    59    61    56
      35  9.24123396  5.35593297         hcp     3    58    59    60
      36  10.62612565  6.15481289         fcc     3    60    62    63
      37  1.60066126  0.94392658          br     2    19    20
      38  2.31102686  2.17441570          br     2    20    21
      39  2.98659056  3.34442654          br     2    21    23
      40  3.02145014  0.94392649          br     2    20    22
      41  3.69695611  4.57491566          br     2    23    24
      42  4.37251986  0.94392657          br     2    25    22
      43  4.37251985  5.74492645          br     2    27    24
      44  4.40737944  3.34442646          br     2    26    23
      45  5.08288547  2.17441570          br     2    25    26
      46  5.08288536  6.97541561          br     1    27
      47  5.75844916  3.34442653          br     2    26    29
      48  5.79330871  0.94392645          br     2    25    28
      49  5.79330869  5.74492636          br     2    27    30
      50  6.46881473  4.57491566          br     2    29    30
      51  7.14437841  0.94392659          br     2    28    31
      52  7.14437845  5.74492645          br     2    30    32
      53  7.17923801  3.34442642          br     2    33    29
      54  7.85474399  2.17441569          br     2    33    31
      55  7.85474398  6.97541561          br     1    32
      56  8.53030771  3.34442655          br     2    33    34
      57  8.56516728  0.94392641          br     1    31
      58  8.56516726  5.74492632          br     2    35    32
      59  9.24067324  4.57491565          br     2    34    35
      60  9.91623700  5.74492647          br     2    35    36
      61  9.95109659  3.34442638          br     1    34
      62  10.62660249  6.97541560          br     1    36
      63  11.33702584  5.74492628          br     1    36
  end_lattice_structure
end_lattice\
"""
    assert( compare( output, expectedOutput, 1e-3 ) )
