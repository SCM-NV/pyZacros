# Execution time: aprox. 50 min
import multiprocessing
import numpy

import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models

scm.pyzacros.init()

# Run as many job simultaneously as there are cpu on the system
maxjobs = multiprocessing.cpu_count()
scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
scm.plams.config.job.runscript.nproc = 1
print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

#---------------------------------------
# Zacros calculation
#---------------------------------------
lh = pz.models.LangmuirHinshelwood()

dt = 1.0e-5
z_sett = pz.Settings()
z_sett.random_seed = 1609
z_sett.temperature = 500.0
z_sett.pressure = 1.000
z_sett.species_numbers = ('time', dt)
z_sett.max_time = 100*dt

z_job = pz.ZacrosJob( settings=z_sett, lattice=lh.lattice,
                      mechanism=lh.mechanism,
                      cluster_expansion=lh.cluster_expansion )

#---------------------------------------
# Steady-State calculation
#---------------------------------------
ss_sett = pz.Settings()
ss_sett.turnover_frequency.nbatch = 20
ss_sett.turnover_frequency.confidence = 0.98
ss_sett.turnover_frequency.ignore_nbatch = 5
ss_sett.nreplicas = 4
ss_sett.scaling.enabled = 'T'
ss_sett.scaling.partial_equilibrium_index_threshold = 0.1
ss_sett.scaling.upper_bound = 100
ss_sett.scaling.max_time = 10*dt

ss_params = pz.ZacrosSteadyStateJob.Parameters()
ss_params.add( 'max_time', 'restart.max_time',
                2*z_sett.max_time*( numpy.arange(50)+1 )**2 )

ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=z_job,
                                  parameters=ss_params )

#---------------------------------------
# Parameters scan calculation
#---------------------------------------
ps_params = pz.ZacrosParametersScanJob.Parameters()
ps_params.add( 'x_CO', 'molar_fraction.CO', numpy.linspace(0.0, 1.0, 21) )
ps_params.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )

ps_job = pz.ZacrosParametersScanJob( reference=ss_job, parameters=ps_params )

results = ps_job.run()

#---------------------------------------------
# Getting the results
#---------------------------------------------
if( results.job.ok() ):
    x_CO = []
    ac_O = []
    ac_CO = []
    TOF_CO2 = []

    results_dict = results.turnover_frequency()
    results_dict = results.average_coverage( last=10, update=results_dict )

    for i in range(len(results_dict)):
        x_CO.append( results_dict[i]['x_CO'] )
        ac_O.append( results_dict[i]['average_coverage']['O*'] )
        ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
        TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )

    print( '------------------------------------------------' )
    print( '%4s'%'cond', '%8s'%'x_CO', '%10s'%'ac_O', '%10s'%'ac_CO', '%12s'%'TOF_CO2' )
    print( '------------------------------------------------' )
    for i in range(len(x_CO)):
        print( '%4d'%i, '%8.2f'%x_CO[i], '%10.6f'%ac_O[i], '%10.6f'%ac_CO[i], '%12.6f'%TOF_CO2[i] )

scm.pyzacros.finish()