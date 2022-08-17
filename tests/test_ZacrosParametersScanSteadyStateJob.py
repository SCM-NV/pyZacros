import numpy
import multiprocessing
import scm.plams

import pyzacros as pz
import pyzacros.models
import pyzacros.utils

def test_ZacrosParametersScanSteadyStateJob():
    print( "----------------------------------------------------------------" )
    print( ">>> Testing ZacrosParametersScanJob(+ZacrosSteadyStateJob) class" )
    print( "----------------------------------------------------------------" )

    lh = pz.models.LangmuirHinshelwood()

    #---------------------------------------------
    # Calculation Settings
    #---------------------------------------------
    scm.plams.init(folder='test_ZacrosParametersScanSteadyStateJob')

    ## Run as many job simultaneously as there are cpu on the system
    #maxjobs = multiprocessing.cpu_count()
    #scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
    #scm.plams.config.job.runscript.nproc = 1
    #print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

    try:
        dt = 5.0e-5

        sett = pz.Settings()
        sett.random_seed = 1609
        sett.temperature = 500.0
        sett.pressure = 1.000
        sett.species_numbers = ('time', dt)
        sett.max_time = 100*dt

        job = pz.ZacrosJob( settings=sett, lattice=lh.lattice, mechanism=lh.mechanism, cluster_expansion=lh.cluster_expansion )

        ss_sett = pz.Settings()
        ss_sett.nreplicas = 2
        ss_sett.turnover_frequency.nbatch = 20
        ss_sett.turnover_frequency.confidence = 0.96
        ss_sett.scaling.max_time = 2*dt
        ss_sett.scaling.partial_equilibrium_index_threshold = 0.1
        ss_sett.scaling.upper_bound = 100

        ss_parameters = { 'max_time':pz.ZacrosSteadyStateJob.Parameter('restart.max_time', 2*sett.max_time*( numpy.arange(20)+1 )**2) }

        ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=job, generator_parameters=ss_parameters, scaling=True )

        parameters = { 'x_CO':pz.ZacrosParametersScanJob.Parameter('molar_fraction.CO', [0.40, 0.50]),
                       'x_O2':pz.ZacrosParametersScanJob.Parameter('molar_fraction.O2', lambda params: 1.0-params['x_CO']) }

        mjob = pz.ZacrosParametersScanJob( reference=ss_job,
                                           generator=pz.ZacrosParametersScanJob.meshGenerator,
                                           generator_parameters=parameters )

        results = mjob.run()

    except pz.ZacrosExecutableNotFoundError:
        print( "Warning: The calculation FAILED because the zacros executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        mjob = scm.plams.load( 'tests/test_ZacrosParametersScanSteadyStateJob.data/plamsjob/plamsjob.dill' )
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

        output += "------------------------------------------------\n"
        output += "%4s"%"cond"+" %8s"%"x_CO"+" %10s"%"ac_O"+" %10s"%"ac_CO"+" %12s"%"TOF_CO2\n"
        output += "------------------------------------------------\n"
        for i in range(len(x_CO)):
            output += "%4d"%i+" %8.2f"%x_CO[i]+" %10.6f"%ac_O[i]+" %10.6f"%ac_CO[i]+" %12.6f"%TOF_CO2[i]+"\n"

    scm.plams.finish()

    print(output)

    expectedOutput = """\
------------------------------------------------
cond     x_CO       ac_O      ac_CO      TOF_CO2
------------------------------------------------
   0     0.40   0.502917   0.213125   278.395749
   1     0.50   0.435833   0.284583   320.506073\
"""

    assert( pz.utils.compare( output, expectedOutput, rel_error=0.1 ) )
