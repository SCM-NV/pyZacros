# Execution time ~1.5h
#
# Questions for Mauro:
# * How can I retrieve the calculated data points?
# * How can I evaluate the Surrogate Model for a given new condition?
# * Can we hide all temporary files generated during the training?

import numpy
import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models
import adaptiveDesignProcedure as adp
import multiprocessing

def getRate( conditions ):

    zgb = pz.models.ZiffGulariBarshad()

    print("")
    print("  Requesting:")
    for cond in conditions:
        print("    xCO = ", cond[0])
    print("")

    #---------------------------------------
    # Zacros calculation
    #---------------------------------------
    z_sett = pz.Settings()
    z_sett.random_seed = 953129
    z_sett.temperature = 500.0
    z_sett.pressure = 1.0
    z_sett.species_numbers = ('time', 0.1)
    z_sett.max_time = 10.0

    z_job = pz.ZacrosJob( settings=z_sett, lattice=zgb.lattice, mechanism=zgb.mechanism,
                          cluster_expansion=zgb.cluster_expansion )

    #---------------------------------------
    # Steady-State calculation
    #---------------------------------------
    ss_sett = pz.Settings()
    ss_sett.turnover_frequency.nbatch = 20
    ss_sett.turnover_frequency.confidence = 0.96
    ss_sett.turnover_frequency.ignore_nbatch = 5
    ss_sett.nreplicas = 4

    ss_parameters = pz.ZacrosSteadyStateJob.Parameters()
    ss_parameters.add( 'max_time', 'restart.max_time', 2*z_sett.max_time*( numpy.arange(100)+1 )**3 )

    ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=z_job, parameters=ss_parameters )

    #---------------------------------------
    # Parameters scan calculation
    #---------------------------------------
    ps_parameters = pz.ZacrosParametersScanJob.Parameters()
    ps_parameters.add( 'x_CO', 'molar_fraction.CO', [ cond[0] for cond in conditions ] )
    ps_parameters.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
    ps_parameters.set_generator( pz.ZacrosParametersScanJob.meshgridGenerator )

    ps_job = pz.ZacrosParametersScanJob( reference=ss_job, parameters=ps_parameters, name='mesh' )

    results = ps_job.run()

    tof = numpy.nan*numpy.empty((len(conditions),1))
    if( results.job.ok() ):
        results_dict = results.turnover_frequency()

        for i in range(len(results_dict)):
            tof[i,0] = results_dict[i]['turnover_frequency']['CO2']

    return tof


scm.pyzacros.init()

# Run as many job simultaneously as there are cpu on the system
maxjobs = multiprocessing.cpu_count()
scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
scm.plams.config.job.runscript.nproc = 1
print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

# Forest parameters
forestParams={
        'Ntree'       : 200,
        'tps'         : 1,
        'fraction'    : 0.9,
    }

# Algorithm paramters
algorithmParams={
        'dth'         : 0.2,     # thresold first derivative
        'd2th'        : 0.8,     # thresold second derivative
        'VIth'        : 0.10,    # thresold variable importance
        'errTh'       : 1e-6,    # thresold for MRE error evaluation (remove from MRE calculation record below this value)
        'OOBth'       : 0.07,    # termination criterium on OOBnorm
        'RADth'       : 70,      # termination criterium on Relative Approximation Error (RAD) [%]
        'maxTDSize'   : 200,     # maximum allowed size of the training data
        'AbsOOBTh'    : 0.2,     # maximum variations between OOB for two different tabulation variables
    }

# Independent and tabulated variables
input_var = ( { 'name' : 'CO', 'min' : 0.001, 'max' : 0.999, 'num' : 5, 'typevar' : 'lin'}, )
tabulation_var = ( {'name' : 'CO2', 'typevar' : 'lin'}, )

# Initialize ADPforML class
adpML = adp.adaptiveDesignProcedure( input_var, tabulation_var, 'ml_ExtraTrees.pkl', 'train.dat',
                                        forestParams, algorithmParams, getRate, benchmark=False )

adpML.createTrainingDataAndML()

scm.plams.finish()
