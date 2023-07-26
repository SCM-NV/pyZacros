import numpy
import multiprocessing
import scm.plams

import scm.pyzacros as pz
import scm.pyzacros.models
import scm.pyzacros.utils


def test_ZacrosParametersScanSteadyStateJob(test_folder, tmp_path):
    print( "----------------------------------------------------------------" )
    print( ">>> Testing ZacrosParametersScanJob(+ZacrosSteadyStateJob) class" )
    print( "----------------------------------------------------------------" )

    lh = pz.models.LangmuirHinshelwood()

    #---------------------------------------------
    # Calculation Settings
    #---------------------------------------------
    scm.plams.init(folder=tmp_path / 'test_ZacrosParametersScanSteadyStateJob')

    ## Run as many job simultaneously as there are cpu on the system
    #maxjobs = multiprocessing.cpu_count()
    #scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
    #scm.plams.config.job.runscript.nproc = 1
    #print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

    try:
        dt = 1.0e-5

        sett = pz.Settings()
        sett.random_seed = 1609
        sett.temperature = 500.0
        sett.pressure = 1.000
        sett.species_numbers = ('time', dt)
        sett.max_time = 100*dt

        job = pz.ZacrosJob( settings=sett, lattice=lh.lattice, mechanism=lh.mechanism, cluster_expansion=lh.cluster_expansion )

        ss_sett = pz.Settings()
        ss_sett.turnover_frequency.nbatch = 20
        ss_sett.turnover_frequency.confidence = 0.96
        ss_sett.turnover_frequency.nreplicas = 2
        ss_sett.scaling.enabled = 'T'
        ss_sett.scaling.partial_equilibrium_index_threshold = 0.1
        ss_sett.scaling.upper_bound = 10
        ss_sett.scaling.max_time = 10*dt
        ss_sett.scaling.species_numbers = ('time', dt)

        ss_parameters = pz.ZacrosSteadyStateJob.Parameters()
        ss_parameters.add( 'max_time', 'restart.max_time', 2*sett.max_time*( numpy.arange(20)+1 )**2 )

        ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=job, parameters=ss_parameters )

        ps_parameters = pz.ZacrosParametersScanJob.Parameters()
        ps_parameters.add( 'x_CO', 'molar_fraction.CO', [0.40, 0.50] )
        ps_parameters.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
        ps_parameters.set_generator( pz.ZacrosParametersScanJob.meshgridGenerator )

        ps_job = pz.ZacrosParametersScanJob( reference=ss_job, parameters=ps_parameters )

        results = ps_job.run()

    except pz.ZacrosExecutableNotFoundError:
        print( "Warning: The calculation FAILED because the zacros executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        ps_job = scm.plams.load( test_folder / 'test_ZacrosParametersScanSteadyStateJob.data/plamsjob/plamsjob.dill' )
        results = ps_job.results

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
   0     0.40   0.512917   0.198542   262.345087
   1     0.50   0.446042   0.253333   301.875030\
"""

    assert( pz.utils.compare( output, expectedOutput, rel_error=0.1 ) )
