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
    sett_ads.input.ams.PESExploration.SaddleSearch.MaxEnergy = 4.0
    sett_ads.input.ams.PESExploration.DynamicSeedStates = 'T'
    sett_ads.input.ams.PESExploration.StructureComparison.DistanceDifference = 0.1
    sett_ads.input.ams.PESExploration.StructureComparison.NeighborCutoff = 3.8
    sett_ads.input.ams.PESExploration.StructureComparison.EnergyDifference = 0.05
    sett_ads.input.ams.PESExploration.StructureComparison.CheckSymmetry = 'T'
    sett_ads.input.ams.PESExploration.CalculateFragments = 'T'
    sett_ads.input.ams.PESExploration.StatesAlignment.ReferenceRegion = 'surface'
    sett_ads.input.ReaxFF.ForceField = 'CHONSFPtClNi.ff'
    sett_ads.input.ReaxFF.Charges.Solver = 'Direct'
    sett_ads.input.ams.Constraints.FixedRegion = 'surface'

    sett_lat = sett_ads.copy()
    sett_lat.input.ams.PESExploration.Job = 'BindingSites'
    sett_lat.input.ams.PESExploration.LoadEnergyLandscape.GenerateSymmetryImages = 'T'
    sett_lat.input.ams.PESExploration.CalculateFragments = 'F'
    sett_lat.input.ams.PESExploration.BindingSites.MaxCoordinationShellsForLabels = 3
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
    loader.replace_site_types( ['N33', 'N331', 'N221'], ['fcc', 'hcp', 'br'] )

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

cluster CO**1fccCO**1fcc:(0,1)
  sites 2
  neighboring 1-2
  lattice_state
    1 CO** 1
    1 CO** 2
  site_types fcc fcc
  graph_multiplicity 2
  cluster_eng -2.08212e+02
end_cluster

cluster CO**1hcpCO**1hcp:(0,1)
  sites 2
  neighboring 1-2
  lattice_state
    1 CO** 1
    1 CO** 2
  site_types hcp hcp
  graph_multiplicity 2
  cluster_eng -2.08210e+02
end_cluster

cluster CO**1brCO**1br:(0,1)
  sites 2
  neighboring 1-2
  lattice_state
    1 CO** 1
    1 CO** 2
  site_types br br
  graph_multiplicity 2
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
  pre_expon  1.92088e+13
  pe_ratio  1.11481e+00
  activ_eng  7.00300e-01
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
  pre_expon  1.92088e+13
  pe_ratio  1.11481e+00
  activ_eng  7.00300e-01
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
  pe_ratio  4.12764e-08
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
  pe_ratio  4.60154e-08
  activ_eng  0.00000e+00
end_reversible_step

reversible_step CO**1hcpCO**1hcp*2br*3br<->*1hcp*2hcpCO**3brCO**3br;(2,3),(0,2),(1,3),(0,1)
  sites 4
  neighboring 3-4 1-3 2-4 1-2
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types hcp hcp br br
  pre_expon  1.58155e+13
  pe_ratio  7.07504e+00
  activ_eng  7.89790e-01
end_reversible_step

reversible_step CO**1hcpCO**1hcp*2br*3br<->*1hcp*2hcpCO**3brCO**3br;(0,1),(0,2),(1,3),(2,3)
  sites 4
  neighboring 1-2 1-3 2-4 3-4
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types hcp hcp br br
  pre_expon  1.58155e+13
  pe_ratio  7.07504e+00
  activ_eng  7.89790e-01
end_reversible_step

reversible_step CO**1hcpCO**1hcp*2br*3br<->*1hcp*2hcpCO**3brCO**3br;(2,3),(1,2),(0,1),(0,3)
  sites 4
  neighboring 3-4 2-3 1-2 1-4
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types hcp hcp br br
  pre_expon  1.58155e+13
  pe_ratio  7.07504e+00
  activ_eng  7.89790e-01
end_reversible_step

reversible_step CO**1hcpCO**1hcp*2br*3br<->*1hcp*2hcpCO**3brCO**3br;(0,1),(0,3),(1,2),(2,3)
  sites 4
  neighboring 1-2 1-4 2-3 3-4
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types hcp hcp br br
  pre_expon  1.58155e+13
  pe_ratio  7.07504e+00
  activ_eng  7.89790e-01
end_reversible_step

reversible_step CO**1hcpCO**1hcp*2br*3br<->*1hcp*2hcpCO**3brCO**3br;(2,3),(0,2),(0,1),(1,3)
  sites 4
  neighboring 3-4 1-3 1-2 2-4
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types hcp hcp br br
  pre_expon  1.58155e+13
  pe_ratio  7.07504e+00
  activ_eng  7.89790e-01
end_reversible_step

reversible_step CO**1hcpCO**1hcp*2br*3br<->*1hcp*2hcpCO**3brCO**3br;(2,3),(1,2),(0,3),(0,1)
  sites 4
  neighboring 3-4 2-3 1-4 1-2
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types hcp hcp br br
  pre_expon  1.58155e+13
  pe_ratio  7.07504e+00
  activ_eng  7.89790e-01
end_reversible_step

reversible_step CO**1hcpCO**1hcp*2br*3br<->*1hcp*2hcpCO**3brCO**3br;(2,3),(1,3),(0,1),(0,2)
  sites 4
  neighboring 3-4 2-4 1-2 1-3
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types hcp hcp br br
  pre_expon  1.58155e+13
  pe_ratio  7.07504e+00
  activ_eng  7.89790e-01
end_reversible_step

reversible_step CO**1hcpCO**1hcp*2br*3br<->*1hcp*2hcpCO**3brCO**3br;(0,1),(1,3),(0,2),(2,3)
  sites 4
  neighboring 1-2 2-4 1-3 3-4
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types hcp hcp br br
  pre_expon  1.58155e+13
  pe_ratio  7.07504e+00
  activ_eng  7.89790e-01
end_reversible_step

reversible_step CO**1fccCO**1fcc*2br*3br<->*1fcc*2fccCO**3brCO**3br;(2,3),(0,2),(1,3),(0,1)
  sites 4
  neighboring 3-4 1-3 2-4 1-2
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types fcc fcc br br
  pre_expon  1.56175e+13
  pe_ratio  7.15629e+00
  activ_eng  7.94879e-01
end_reversible_step

reversible_step CO**1fccCO**1fcc*2br*3br<->*1fcc*2fccCO**3brCO**3br;(0,1),(0,2),(1,3),(2,3)
  sites 4
  neighboring 1-2 1-3 2-4 3-4
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types fcc fcc br br
  pre_expon  1.56175e+13
  pe_ratio  7.15629e+00
  activ_eng  7.94879e-01
end_reversible_step

reversible_step CO**1fccCO**1fcc*2br*3br<->*1fcc*2fccCO**3brCO**3br;(0,1),(0,3),(1,2),(2,3)
  sites 4
  neighboring 1-2 1-4 2-3 3-4
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types fcc fcc br br
  pre_expon  1.56175e+13
  pe_ratio  7.15629e+00
  activ_eng  7.94879e-01
end_reversible_step

reversible_step CO**1fccCO**1fcc*2br*3br<->*1fcc*2fccCO**3brCO**3br;(2,3),(1,2),(0,3),(0,1)
  sites 4
  neighboring 3-4 2-3 1-4 1-2
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types fcc fcc br br
  pre_expon  1.56175e+13
  pe_ratio  7.15629e+00
  activ_eng  7.94879e-01
end_reversible_step

reversible_step CO**1fccCO**1fcc*2br*3br<->*1fcc*2fccCO**3brCO**3br;(0,1),(0,2),(2,3),(1,3)
  sites 4
  neighboring 1-2 1-3 3-4 2-4
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types fcc fcc br br
  pre_expon  1.56175e+13
  pe_ratio  7.15629e+00
  activ_eng  7.94879e-01
end_reversible_step

reversible_step CO**1fccCO**1fcc*2br*3br<->*1fcc*2fccCO**3brCO**3br;(2,3),(0,2),(0,1),(1,3)
  sites 4
  neighboring 3-4 1-3 1-2 2-4
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types fcc fcc br br
  pre_expon  1.56175e+13
  pe_ratio  7.15629e+00
  activ_eng  7.94879e-01
end_reversible_step

reversible_step CO**1fccCO**1fcc*2br*3br<->*1fcc*2fccCO**3brCO**3br;(2,3),(1,3),(0,1),(0,2)
  sites 4
  neighboring 3-4 2-4 1-2 1-3
  initial
    1 CO** 1
    1 CO** 2
    2 * 1
    3 * 1
  final
    1 * 1
    2 * 1
    3 CO** 1
    3 CO** 2
  site_types fcc fcc br br
  pre_expon  1.56175e+13
  pe_ratio  7.15629e+00
  activ_eng  7.94879e-01
end_reversible_step

reversible_step CO**1fccCO**1fcc<->*1fcc*2fcc:CO;(0,1)
  gas_reacs_prods CO -1
  sites 2
  neighboring 1-2
  initial
    1 * 1
    2 * 1
  final
    1 CO** 1
    1 CO** 2
  site_types fcc fcc
  pre_expon  8.05092e+06
  pe_ratio  4.84689e-10
  activ_eng  0.00000e+00
end_reversible_step

reversible_step CO**1hcpCO**1hcp<->*1hcp*2hcp:CO;(0,1)
  gas_reacs_prods CO -1
  sites 2
  neighboring 1-2
  initial
    1 * 1
    2 * 1
  final
    1 CO** 1
    1 CO** 2
  site_types hcp hcp
  pre_expon  8.05092e+06
  pe_ratio  4.90255e-10
  activ_eng  0.00000e+00
end_reversible_step

reversible_step CO**1brCO**1br<->*1br*2br:CO;(0,1)
  gas_reacs_prods CO -1
  sites 2
  neighboring 1-2
  initial
    1 * 1
    2 * 1
  final
    1 CO** 1
    1 CO** 2
  site_types br br
  pre_expon  8.05092e+06
  pe_ratio  3.46858e-09
  activ_eng  0.00000e+00
end_reversible_step

end_mechanism

lattice explicit
  cell_vectors
  8.31557575  0.00000000
  4.15778787  7.20149984
  n_sites 45
  max_coord 7
  n_site_types 3
  site_type_names br fcc hcp
  lattice_structure
       1       0.92536499       0.55407797         hcp     3     1     2    19
       2       2.31078049       1.35400906         fcc     7     1     2     3     4    19    20    21
       3       2.31129428       2.95457792         hcp     5     2     3     5    20    22
       4       3.69722357       0.55407797         hcp     5     2     4     7    21    24
       5       3.69670978       3.75450901         fcc     7     3     5     6     8    22    23    25
       6       3.69722357       5.35507786         hcp     5     5     6     9    23    26
       7       5.08263907       1.35400906         fcc     7     4     7     8    10    24    27    30
       8       5.08315286       2.95457792         hcp     7     5     7     8    11    25    27    29
       9       5.08263907       6.15500895         fcc     6     6     9    12    26    28    31
      10       6.46908215       0.55407797         hcp     5    33     7    10    13    30
      11       6.46856836       3.75450901         fcc     7    35     8    11    12    14    29    32
      12       6.46908215       5.35507786         hcp     7    34     9    11    12    15    31    32
      13       7.85449765       1.35400906         fcc     6    33    36    39    10    13    14
      14       7.85501144       2.95457792         hcp     7    35    36    38    11    13    14    16
      15       7.85449765       6.15500895         fcc     6    34    37    40    12    15    17
      16       9.24042694       3.75450901         fcc     6    38    41    42    14    16    17
      17       9.24094073       5.35507786         hcp     7    40    41    43    15    16    17    18
      18      10.62635623       6.15500895         fcc     5    43    44    45    17    18
      19       1.60537530       0.94674101          br     3     1     2    19
      20       2.31110738       2.16892614          br     3     2     3    20
      21       3.01673630       0.94674101          br     3     2     4    21
      22       2.99130459       3.34724096          br     3     3     5    22
      23       3.69703667       4.56942609          br     3     5     6    23
      24       4.37723388       0.94674101          br     3     4     7    24
      25       4.40266559       3.34724096          br     3    25     5     8
      26       4.37723388       5.74774090          br     3     9    26     6
      27       5.08296596       2.16892614          br     3    27     7     8
      28       5.08296596       6.96992603          br     2     9    28
      29       5.76316317       3.34724096          br     3    11    29     8
      30       5.78859488       0.94674101          br     3    10    30     7
      31       5.78859488       5.74774090          br     3     9    12    31
      32       6.46889525       4.56942609          br     3    11    12    32
      33       7.11705558       0.92865824          br     3    33    10    13
      34       7.11705558       5.72965813          br     3    34    12    15
      35       7.17452417       3.34724096          br     3    35    11    14
      36       7.85482455       2.16892614          br     3    36    13    14
      37       7.85482454       6.96992603          br     2    37    15
      38       8.50298487       3.32915819          br     3    38    14    16
      39       8.56045347       0.94674101          br     2    13    39
      40       8.56045346       5.74774090          br     3    17    15    40
      41       9.24075384       4.56942609          br     3    17    41    16
      42       9.94638276       3.34724096          br     2    42    16
      43       9.92095104       5.74774090          br     3    17    18    43
      44      10.62668313       6.96992603          br     2    18    44
      45      11.33231205       5.74774090          br     2    18    45
  end_lattice_structure
end_lattice\
"""
    assert( pz.utils.compare( output, expectedOutput, abs_error=1e-12, rel_error=0.1 ) )
