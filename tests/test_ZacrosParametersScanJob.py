import numpy
import multiprocessing
import scm.plams

import pyzacros as pz
import pyzacros.models
import pyzacros.utils

def test_ZacrosParametersScanJob():
    print( "---------------------------------------------------" )
    print( ">>> Testing ZacrosParametersScanJob class" )
    print( "---------------------------------------------------" )

    zgb = pz.models.ZiffGulariBarshad()

    #---------------------------------------------
    # Calculation Settings
    #---------------------------------------------
    scm.plams.init(folder='test_ZacrosParametersScanJob')

    ## Run as many job simultaneously as there are cpu on the system
    #maxjobs = multiprocessing.cpu_count()
    #scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
    #scm.plams.config.job.runscript.nproc = 1
    #print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

    # Settings:
    sett = pz.Settings()
    sett.random_seed = 953129
    sett.temperature = 500.0
    sett.pressure = 1.0
    sett.snapshots = ('time', 2.0)
    sett.species_numbers = ('time', 0.1)
    sett.max_time = 10.0

    # This is to be used in combination with: generator=pz.ZacrosParametersScanJob.meshGenerator
    parameters = { 'x_CO':pz.ZacrosParametersScanJob.Parameter('molar_fraction.CO', numpy.arange(0.2, 0.8, 0.1)),
                   'x_O2':pz.ZacrosParametersScanJob.Parameter('molar_fraction.O2', lambda params: 1.0-params['x_CO']) }

    # This is to be used in combination with: generator=pz.ZacrosParametersScanJob.zipGenerator
    #parameters = { 'x_CO':pz.ZacrosParametersScanJob.Parameter('molar_fraction.CO', numpy.arange(0.2, 0.8, 0.1)),
                   #'x_O2':pz.ZacrosParametersScanJob.Parameter('molar_fraction.O2', 1.0-numpy.arange(0.2, 0.8, 0.1)) }

    try:
        job = pz.ZacrosJob( settings=sett, lattice=zgb.lattice, mechanism=zgb.mechanism,
                            cluster_expansion=zgb.cluster_expansion )

        mjob = pz.ZacrosParametersScanJob( reference=job,
                                           generator=pz.ZacrosParametersScanJob.meshGenerator,
                                           generator_parameters=parameters )

        results = mjob.run()

    except pz.ZacrosExecutableNotFoundError:
        print( "Warning: The calculation FAILED because the zacros executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        mjob = scm.plams.load( 'tests/test_ZacrosParametersScanJob.data/plamsjob/plamsjob.dill' )
        results = mjob.results

    output = ""

    if( results.job.ok() ):
        x_CO = []
        ac_O = []
        ac_CO = []
        TOF_CO2 = []

        results_dict = results.turnover_frequency()
        results_dict = results.average_coverage( last=3, update=results_dict )

        for i in range(len(results_dict)):
            x_CO.append( results_dict[i]['x_CO'] )
            ac_O.append( results_dict[i]['average_coverage']['O*'] )
            ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
            TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )

        output += "----------------------------------------------\n"
        output += "%4s"%"cond"+" %8s"%"x_CO"+" %10s"%"ac_O"+" %10s"%"ac_CO"+" %10s"%"TOF_CO2\n"
        output += "----------------------------------------------\n"
        for i in range(len(x_CO)):
            output += "%4d"%i+" %8.2f"%x_CO[i]+" %10.6f"%ac_O[i]+" %10.6f"%ac_CO[i]+" %10.6f"%TOF_CO2[i]+"\n"

    scm.plams.finish()

    print(output)

    expectedOutput = """\
----------------------------------------------
cond     x_CO       ac_O      ac_CO   TOF_CO2
----------------------------------------------
   0     0.20   0.997867   0.000000   0.004800
   1     0.30   0.995733   0.000000   0.008800
   2     0.40   0.903333   0.000533   0.413600
   3     0.50   0.565733   0.024400   2.034400
   4     0.60   0.000000   1.000000   0.000000
   5     0.70   0.000000   1.000000   0.000000
   6     0.80   0.000000   1.000000   0.000000\
"""

    assert( pz.utils.compare( output, expectedOutput, rel_error=0.1 ) )
