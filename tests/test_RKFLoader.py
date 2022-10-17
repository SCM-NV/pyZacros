import os
import sys
import shutil

import scm.plams

import scm.pyzacros as pz
import scm.pyzacros.utils


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
        jobO_lat = scm.plams.load( "tests/test_RKFLoader.data/O-Pt111/O-Pt111.dill" )
        jobCO_lat = scm.plams.load( "tests/test_RKFLoader.data/CO-Pt111/CO-Pt111.dill" )

    return jobO_lat.results,jobCO_lat.results


def test_RKFLoader():
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

cluster O*fcc
  sites 1
  lattice_state
    1 O* 1
  site_types fcc
  graph_multiplicity 1
  cluster_eng -1.98060e+02
end_cluster

cluster O*hcp
  sites 1
  lattice_state
    1 O* 1
  site_types hcp
  graph_multiplicity 1
  cluster_eng -1.97861e+02
end_cluster

cluster CO*fcc
  sites 1
  lattice_state
    1 CO* 1
  site_types fcc
  graph_multiplicity 1
  cluster_eng -2.08212e+02
end_cluster

cluster CO*hcp
  sites 1
  lattice_state
    1 CO* 1
  site_types hcp
  graph_multiplicity 1
  cluster_eng -2.08210e+02
end_cluster

cluster CO*br
  sites 1
  lattice_state
    1 CO* 1
  site_types br
  graph_multiplicity 1
  cluster_eng -2.07455e+02
end_cluster

end_energetics

mechanism

reversible_step O*1hcp*2fcc<->*1hcpO*2fcc;(0,1)
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

reversible_step O*1fcc*2hcp<->*1fccO*2hcp;(0,1)
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

reversible_step O*fcc<->*fcc:O
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

reversible_step O*hcp<->*hcp:O
  gas_reacs_prods O -1
  sites 1
  initial
    1 * 1
  final
    1 O* 1
  site_types hcp
  pre_expon  1.06511e+07
  pe_ratio  4.60157e-08
  activ_eng  0.00000e+00
end_reversible_step

reversible_step CO*1hcp*2br<->*1hcpCO*2br;(0,1)
  sites 2
  neighboring 1-2
  initial
    1 CO* 1
    2 * 1
  final
    1 * 1
    2 CO* 1
  site_types hcp br
  pre_expon  1.57247e+13
  pe_ratio  7.07192e+00
  activ_eng  7.89789e-01
end_reversible_step

reversible_step CO*1fcc*2br<->*1fccCO*2br;(0,1)
  sites 2
  neighboring 1-2
  initial
    1 CO* 1
    2 * 1
  final
    1 * 1
    2 CO* 1
  site_types fcc br
  pre_expon  1.57050e+13
  pe_ratio  7.15381e+00
  activ_eng  7.94878e-01
end_reversible_step

reversible_step CO*fcc<->*fcc:CO
  gas_reacs_prods CO -1
  sites 1
  initial
    1 * 1
  final
    1 CO* 1
  site_types fcc
  pre_expon  8.05092e+06
  pe_ratio  1.23247e-24
  activ_eng  0.00000e+00
end_reversible_step

reversible_step CO*hcp<->*hcp:CO
  gas_reacs_prods CO -1
  sites 1
  initial
    1 * 1
  final
    1 CO* 1
  site_types hcp
  pre_expon  8.05092e+06
  pe_ratio  1.24673e-24
  activ_eng  0.00000e+00
end_reversible_step

reversible_step CO*br<->*br:CO
  gas_reacs_prods CO -1
  sites 1
  initial
    1 * 1
  final
    1 CO* 1
  site_types br
  pre_expon  8.05092e+06
  pe_ratio  8.81691e-24
  activ_eng  0.00000e+00
end_reversible_step

end_mechanism

lattice explicit
  cell_vectors
  8.31557575  0.00000000
  4.15778787  7.20149984
  n_sites 45
  max_coord 6
  n_site_types 3
  site_type_names br fcc hcp
  lattice_structure
       1       0.92536450       0.55407768         hcp     2     2    19
       2       2.31078110       1.35400928         fcc     6     1     3     4    19    20    21
       3       2.31129379       2.95457763         hcp     4     2    20     5    22
       4       3.69722308       0.55407768         hcp     4     2    21     7    24
       5       3.69671039       3.75450923         fcc     6     3     6     8    22    23    25
       6       3.69722308       5.35507757         hcp     4     9    26     5    23
       7       5.08263968       1.35400928         fcc     6     4     8    10    24    27    29
       8       5.08315237       2.95457763         hcp     6     5     7    11    25    27    30
       9       5.08263968       6.15500917         fcc     5     6    12    26    28    31
      10       6.46908166       0.55407768         hcp     4    33    13    29     7
      11       6.46856897       3.75450923         fcc     6    34     8    12    14    30    32
      12       6.46908166       5.35507757         hcp     6    35     9    11    15    31    32
      13       7.85449826       1.35400928         fcc     5    33    36    38    10    14
      14       7.85501095       2.95457763         hcp     6    34    36    39    11    13    16
      15       7.85449826       6.15500917         fcc     5    35    37    40    12    17
      16       9.24042755       3.75450923         fcc     5    39    41    42    14    17
      17       9.24094024       5.35507757         hcp     6    40    41    43    15    16    18
      18      10.62635684       6.15500917         fcc     4    17    43    44    45
      19       1.60537481       0.94674127          br     2     1     2
      20       2.31110785       2.16892643          br     2     2     3
      21       3.01673678       0.94674127          br     2     2     4
      22       2.99130410       3.34724122          br     2     3     5
      23       3.69703714       4.56942638          br     2     5     6
      24       4.37723339       0.94674127          br     2     4     7
      25       4.40266607       3.34724122          br     2     5     8
      26       4.37723339       5.74774116          br     2     9     6
      27       5.08296643       2.16892643          br     2     7     8
      28       5.08296643       6.96992632          br     1     9
      29       5.78859536       0.94674127          br     2    10     7
      30       5.76316268       3.34724122          br     2    11     8
      31       5.78859536       5.74774116          br     2     9    12
      32       6.46889572       4.56942638          br     2    11    12
      33       7.14909197       0.94674127          br     2    10    13
      34       7.17452465       3.34724122          br     2    11    14
      35       7.14909197       5.74774116          br     2    12    15
      36       7.85482502       2.16892643          br     2    13    14
      37       7.85482501       6.96992632          br     1    15
      38       8.56045395       0.94674127          br     1    13
      39       8.53502126       3.34724122          br     2    14    16
      40       8.56045394       5.74774116          br     2    17    15
      41       9.24075431       4.56942638          br     2    17    16
      42       9.94638324       3.34724122          br     1    16
      43       9.92095055       5.74774116          br     2    17    18
      44      10.62668360       6.96992632          br     1    18
      45      11.33231253       5.74774116          br     1    18
  end_lattice_structure
end_lattice\
"""
    assert( pz.utils.compare( output, expectedOutput, abs_error=1e-12, rel_error=0.1 ) )
