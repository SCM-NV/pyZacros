import numpy
import multiprocessing
from collections import UserList

import scm.plams

import scm.pyzacros as pz
import scm.pyzacros.models
import scm.pyzacros.utils


def test_ZacrosParametersScanJob(test_folder, tmp_path):
    print("---------------------------------------------------")
    print(">>> Testing ZacrosParametersScanJob class")
    print("---------------------------------------------------")

    zgb = pz.models.ZiffGulariBarshad()

    # ---------------------------------------------
    # Calculation Settings
    # ---------------------------------------------
    scm.plams.init(folder=tmp_path / "test_ZacrosParametersScanJob")

    ## Run as many job simultaneously as there are cpu on the system
    # maxjobs = multiprocessing.cpu_count()
    # scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
    # scm.plams.config.job.runscript.nproc = 1
    # print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

    # Settings:
    sett = pz.Settings()
    sett.random_seed = 953129
    sett.temperature = 500.0
    sett.pressure = 1.0
    sett.snapshots = ("time", 2.0)
    sett.species_numbers = ("time", 0.1)
    sett.max_time = 10.0

    parameters = pz.ZacrosParametersScanJob.Parameters()
    parameters.add("x_CO", "molar_fraction.CO", numpy.arange(0.2, 0.8, 0.1))
    parameters.add("x_O2", "molar_fraction.O2", lambda params: 1.0 - params["x_CO"])
    parameters.set_generator(pz.ZacrosParametersScanJob.meshgridGenerator)

    try:
        job = pz.ZacrosJob(
            settings=sett, lattice=zgb.lattice, mechanism=zgb.mechanism, cluster_expansion=zgb.cluster_expansion
        )

        mjob = pz.ZacrosParametersScanJob(reference=job, parameters=parameters)

        results = mjob.run()

    except pz.ZacrosExecutableNotFoundError:
        print("Warning: The calculation FAILED because the zacros executable is not available!")
        print("         For testing purposes, now we load precalculated results.")

        mjob = scm.plams.load(test_folder / "test_ZacrosParametersScanJob.data/plamsjob/plamsjob.dill")
        results = mjob.results

    output = ""

    if results.job.ok():
        x_CO = []
        ac_O = []
        ac_CO = []
        TOF_CO2 = []

        results_dict = results.turnover_frequency()
        results_dict = results.average_coverage(last=3, update=results_dict)

        for i in range(len(results_dict)):
            x_CO.append(results_dict[i]["x_CO"])
            ac_O.append(results_dict[i]["average_coverage"]["O*"])
            ac_CO.append(results_dict[i]["average_coverage"]["CO*"])
            TOF_CO2.append(results_dict[i]["turnover_frequency"]["CO2"])

        output += "----------------------------------------------\n"
        output += "%4s" % "cond" + " %8s" % "x_CO" + " %10s" % "ac_O" + " %10s" % "ac_CO" + " %10s" % "TOF_CO2\n"
        output += "----------------------------------------------\n"
        for i in range(len(x_CO)):
            output += (
                "%4d" % i
                + " %8.2f" % x_CO[i]
                + " %10.6f" % ac_O[i]
                + " %10.6f" % ac_CO[i]
                + " %10.6f" % TOF_CO2[i]
                + "\n"
            )

    scm.plams.finish()

    print(output)

    expectedOutput = """\
----------------------------------------------
cond     x_CO       ac_O      ac_CO   TOF_CO2
----------------------------------------------
   0     0.20   0.997867   0.000000   0.049895
   1     0.30   0.995733   0.000000   0.123811
   2     0.40   0.903333   0.000533   0.577095
   3     0.50   0.565733   0.024400   2.108442
   4     0.60   0.000000   1.000000   0.221453
   5     0.70   0.000000   1.000000   0.008863
   6     0.80   0.000000   1.000000   0.000589\
"""

    assert pz.utils.compare(output, expectedOutput, rel_error=0.1)
