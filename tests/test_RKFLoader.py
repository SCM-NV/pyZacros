import os
import sys
import shutil

import scm.plams

import scm.pyzacros as pz
import scm.pyzacros.utils


def generateAMSResults(test_folder):
    """Generates of the energy landscape for the O-Pt111 system"""

    sett_ads = scm.plams.Settings()
    sett_ads.input.ams.Task = "PESExploration"
    sett_ads.input.ams.PESExploration.Job = "ProcessSearch"
    sett_ads.input.ams.PESExploration.RandomSeed = 100
    sett_ads.input.ams.PESExploration.NumExpeditions = 10
    sett_ads.input.ams.PESExploration.NumExplorers = 4
    sett_ads.input.ams.PESExploration.Optimizer.ConvergedForce = 0.0005
    sett_ads.input.ams.PESExploration.SaddleSearch.MaxEnergy = 4.0
    sett_ads.input.ams.PESExploration.DynamicSeedStates = "T"
    sett_ads.input.ams.PESExploration.StructureComparison.DistanceDifference = 0.1
    sett_ads.input.ams.PESExploration.StructureComparison.EnergyDifference = 0.5
    sett_ads.input.ams.PESExploration.StructureComparison.CheckSymmetry = "T"
    sett_ads.input.ams.PESExploration.CalculateFragments = "T"
    sett_ads.input.ams.PESExploration.StatesAlignment.ReferenceRegion = "surface"
    sett_ads.input.ReaxFF.ForceField = "CHONSFPtClNi.ff"
    sett_ads.input.ReaxFF.Charges.Solver = "Direct"
    sett_ads.input.ams.Constraints.FixedRegion = "surface"

    sett_lat = sett_ads.copy()
    sett_lat.input.ams.PESExploration.Job = "BindingSites"
    sett_lat.input.ams.PESExploration.LoadEnergyLandscape.GenerateSymmetryImages = "T"
    sett_lat.input.ams.PESExploration.CalculateFragments = "F"
    sett_lat.input.ams.PESExploration.BindingSites.NeighborCutoff = 2.9
    sett_lat.input.ams.PESExploration.StructureComparison.CheckSymmetry = "F"

    molO = scm.plams.Molecule(test_folder / "O-Pt111.xyz")
    molCO = scm.plams.Molecule(test_folder / "CO-Pt111.xyz")

    jobO_ads = scm.plams.AMSJob(molecule=molO, settings=sett_ads, name="O_ads-Pt111")
    jobCO_ads = scm.plams.AMSJob(molecule=molCO, settings=sett_ads, name="CO_ads-Pt111")

    sett_lat.input.ams.PESExploration.LoadEnergyLandscape.Path = "../O_ads-Pt111"
    jobO_lat = scm.plams.AMSJob(molecule=molO, settings=sett_lat, name="O-Pt111", depend=[jobO_ads])

    sett_lat.input.ams.PESExploration.LoadEnergyLandscape.Path = "../CO_ads-Pt111"
    jobCO_lat = scm.plams.AMSJob(molecule=molCO, settings=sett_lat, name="CO-Pt111", depend=[jobCO_ads])

    jobs = [jobO_ads, jobCO_ads, jobO_lat, jobCO_lat]

    for job in jobs:
      job.run()

    success = True
    for job in jobs:
      if not job.ok() and "AMSBIN" not in os.environ:
        print("Warning: The calculation FAILED likely because AMS executable is not available!")
        print("         For testing purposes, now we load precalculated results.")
        success = False

    if success:
      scm.plams.delete_job(jobO_ads)
      scm.plams.delete_job(jobCO_ads)
    else:
      jobO_lat = scm.plams.load(test_folder / "test_RKFLoader.data/O-Pt111/O-Pt111.dill")
      jobCO_lat = scm.plams.load(test_folder / "test_RKFLoader.data/CO-Pt111/CO-Pt111.dill")

    return jobO_lat.results, jobCO_lat.results


def test_RKFLoader(test_folder, tmp_path):
    print("---------------------------------------------------")
    print(">>> Testing RKFLoader class")
    print("---------------------------------------------------")

    workdir = tmp_path / "test_RKFLoader"
    scm.plams.init(folder=str(workdir))

    resultsO, resultsCO = generateAMSResults(test_folder=test_folder)

    scm.plams.finish()

    loaderO = pz.RKFLoader(resultsO)
    loaderCO = pz.RKFLoader(resultsCO)

    loader = pz.RKFLoader.merge([loaderO, loaderCO])
    loader.replace_site_types(["N333", "N331", "N221"], ["fcc", "hcp", "br"])

    output = str(loader.clusterExpansion) + "\n\n"
    output += str(loader.mechanism) + "\n\n"

    loader.lattice.set_repeat_cell([2, 2])
    loader.lattice.plot(pause=2)

    output += str(loader.lattice)

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

reversible_step O*1fcc*2hcp<->*1fccO*2hcp;(0,1)
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

reversible_step CO*1br*2hcp<->*1brCO*2hcp;(0,1)
  sites 2
  neighboring 1-2
  initial
    1 CO* 1
    2 * 1
  final
    1 * 1
    2 CO* 1
  site_types hcp br
  pre_expon  1.62480e+13
  pe_ratio  7.00877e+00
  activ_eng  7.89803e-01
end_reversible_step

reversible_step CO*1br*2fcc<->*1brCO*2fcc;(0,1)
  sites 2
  neighboring 1-2
  initial
    1 CO* 1
    2 * 1
  final
    1 * 1
    2 CO* 1
  site_types fcc br
  pre_expon  1.57198e+13
  pe_ratio  7.11488e+00
  activ_eng  7.94882e-01
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
  pe_ratio  4.82946e-10
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
  pe_ratio  4.90258e-10
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
  pe_ratio  3.43610e-09
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
       1       0.92536499       0.55407797         hcp     2     2    19
       2       2.31078049       1.35400906         fcc     6     1     3     4    19    20    21
       3       2.31129428       2.95457792         hcp     4     2    20     5    22
       4       3.69722357       0.55407797         hcp     4     2    21     7    24
       5       3.69670978       3.75450901         fcc     6     3     6     8    22    23    25
       6       3.69722357       5.35507786         hcp     4     9    26     5    23
       7       5.08263907       1.35400906         fcc     6     4     8    10    24    27    29
       8       5.08315286       2.95457792         hcp     6     5     7    11    25    27    30
       9       5.08263907       6.15500895         fcc     5     6    12    26    28    31
      10       6.46908215       0.55407797         hcp     4    33    13    29     7
      11       6.46856836       3.75450901         fcc     6    34     8    12    14    30    32
      12       6.46908215       5.35507786         hcp     6    35     9    11    15    31    32
      13       7.85449765       1.35400906         fcc     5    33    36    38    10    14
      14       7.85501144       2.95457792         hcp     6    34    36    39    11    13    16
      15       7.85449765       6.15500895         fcc     5    35    37    40    12    17
      16       9.24042694       3.75450901         fcc     5    39    41    42    14    17
      17       9.24094073       5.35507786         hcp     6    40    41    43    15    16    18
      18      10.62635623       6.15500895         fcc     4    17    43    44    45
      19       1.60401619       0.94611082          br     2     1     2
      20       2.31124118       2.17041826          br     2     2     3
      21       3.01809541       0.94611082          br     2     2     4
      22       2.98994548       3.34661077          br     2     3     5
      23       3.69717047       4.57091821          br     2     5     6
      24       4.37587477       0.94611082          br     2     4     7
      25       4.40402470       3.34661077          br     2     5     8
      26       4.37587477       5.74711071          br     2     9     6
      27       5.08309976       2.17041826          br     2     7     8
      28       5.08309976       6.97141815          br     1     9
      29       5.78995399       0.94611082          br     2    10     7
      30       5.76180406       3.34661077          br     2    11     8
      31       5.78995399       5.74711071          br     2     9    12
      32       6.46902905       4.57091821          br     2    11    12
      33       7.14773335       0.94611082          br     2    10    13
      34       7.17588328       3.34661077          br     2    11    14
      35       7.14773335       5.74711071          br     2    12    15
      36       7.85495835       2.17041826          br     2    13    14
      37       7.85495834       6.97141815          br     1    15
      38       8.56181258       0.94611082          br     1    13
      39       8.53366264       3.34661077          br     2    14    16
      40       8.56181257       5.74711071          br     2    17    15
      41       9.24088764       4.57091821          br     2    17    16
      42       9.94774187       3.34661077          br     1    16
      43       9.91959193       5.74711071          br     2    17    18
      44      10.62681693       6.97141815          br     1    18
      45      11.33367116       5.74711071          br     1    18
  end_lattice_structure
end_lattice\
"""
    assert pz.utils.compare(output, expectedOutput, abs_error=1e-12, rel_error=0.1)
