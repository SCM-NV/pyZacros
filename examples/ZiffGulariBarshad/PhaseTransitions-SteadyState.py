# Execution time ~5min

import numpy
import multiprocessing

import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models

zgb = pz.models.ZiffGulariBarshad()

scm.plams.init()

# Run as many job simultaneously as there are cpu on the system
maxjobs = multiprocessing.cpu_count()
scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
scm.plams.config.job.runscript.nproc = 1
print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

z_sett = pz.Settings()
z_sett.random_seed = 953129
z_sett.temperature = 500.0
z_sett.pressure = 1.0
z_sett.species_numbers = ('time', 0.1)
z_sett.max_time = 10.0

z_job = pz.ZacrosJob( settings=z_sett, lattice=zgb.lattice, mechanism=zgb.mechanism,
                      cluster_expansion=zgb.cluster_expansion )

ss_sett = pz.Settings()
ss_sett.turnover_frequency.nbatch = 20
ss_sett.turnover_frequency.confidence = 0.96
ss_sett.turnover_frequency.ignore_nbatch = 5
ss_sett.nreplicas = 4

ss_parameters = pz.ZacrosSteadyStateJob.Parameters()
ss_parameters.add( 'max_time', 'restart.max_time', 2*z_sett.max_time*( numpy.arange(20)+1 )**3 )

ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=z_job, parameters=ss_parameters )

ps_parameters = pz.ZacrosParametersScanJob.Parameters()
ps_parameters.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.2, 0.8, 0.01) )
ps_parameters.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
ps_parameters.set_generator( pz.ZacrosParametersScanJob.meshgridGenerator )

ps_job = pz.ZacrosParametersScanJob( reference=ss_job, parameters=ps_parameters, name='mesh' )

results = ps_job.run()

x_CO = []
ac_O = []
ac_CO = []
TOF_CO2 = []
max_time = []

if( results.job.ok() ):
    results_dict = results.turnover_frequency()
    results_dict = results.average_coverage( last=20, update=results_dict )
    cresults = results.children_results()

    for i in range(len(results_dict)):
        x_CO.append( results_dict[i]['x_CO'] )
        ac_O.append( results_dict[i]['average_coverage']['O*'] )
        ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
        TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )
        max_time.append( results.children_results( child_id=(i,) ).history( pos=-1 )['max_time'] )

    print( "-----------------------------------------------------------" )
    print( "%4s"%"cond", " %8s"%"x_CO", " %10s"%"ac_O", "%10s"%"ac_CO", "%12s"%"TOF_CO2", "%10s"%"max_time" )
    print( "-----------------------------------------------------------" )
    for i in range(len(x_CO)):
        print( "%4d"%i, "%8.2f"%x_CO[i], "%10.6f"%ac_O[i], "%10.6f"%ac_CO[i], "%12.6f"%TOF_CO2[i], "%10.3f"%max_time[i] )

scm.plams.finish()

#---------------------------------------------
# Plotting the results
#---------------------------------------------
try:
    import matplotlib.pyplot as plt
except ImportError as e:
    print('Consider to install matplotlib to visualize the results!')
    exit(0)

# Coverage and TOF plot
fig = plt.figure()

ax = plt.axes()
ax.set_xlabel('Partial Pressure CO', fontsize=14)
ax.set_ylabel("Coverage Fraction (%)", color="blue", fontsize=14)
ax.plot(x_CO, ac_O, color="blue", linestyle="-.", lw=2, zorder=1)
ax.plot(x_CO, ac_CO, color="blue", linestyle="-", lw=2, zorder=2)
plt.text(0.3, 0.9, 'O', fontsize=18, color="blue")
plt.text(0.7, 0.9, 'CO', fontsize=18, color="blue")

ax2 = ax.twinx()
ax2.set_ylabel("TOF (mol/s/site)",color="red", fontsize=14)
ax2.plot(x_CO, TOF_CO2, color="red", lw=2, zorder=5)
plt.text(0.37, 1.5, 'CO$_2$', fontsize=18, color="red")

plt.show()
